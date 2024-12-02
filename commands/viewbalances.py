from telegram import Update
from telegram.ext import ContextTypes
from utils import load_data

async def view_balances(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /view_balances <group_name>")
        return

    group_name = " ".join(args)
    data = load_data()

    # Find the group by name
    group_id = next((gid for gid, g in data["groups"].items() if g["name"] == group_name), None)
    if not group_id:
        await update.message.reply_text("Group not found!")
        return

    # Display balances
    balances = data["groups"][group_id]["balances"]
    balance_message = f"Balances for group '{group_name}':\n"
    for user_id, balance in balances.items():
        username = data["users"].get(user_id, {}).get("username", "Unknown User")
        balance_message += f"{username}: ${balance:.2f}\n"

    await update.message.reply_text(balance_message)
