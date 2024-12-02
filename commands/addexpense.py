from telegram import Update
from telegram.ext import ContextTypes
from utils import load_data, save_data

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("Usage: /add_expense <group_name> <amount> <description>")
        return

    group_name, amount, *description = args
    description = " ".join(description)
    user_id = str(update.message.from_user.id)

    data = load_data()

    # Find the group by name
    group_id = next((gid for gid, g in data["groups"].items() if g["name"] == group_name), None)
    if not group_id:
        await update.message.reply_text("Group not found!")
        return

    # Ensure the user is a member of the group
    if user_id not in data["groups"][group_id]["members"]:
        await update.message.reply_text("You are not a member of this group!")
        return

    # Add the expense
    amount = float(amount)
    data["groups"][group_id]["expenses"].append({
        "payer": user_id,
        "amount": amount,
        "description": description
    })

    # Split the expense among group members
    members = data["groups"][group_id]["members"]
    split_amount = amount / len(members)
    for member in members:
        data["groups"][group_id]["balances"][member] += split_amount
    data["groups"][group_id]["balances"][user_id] -= amount

    save_data(data)
    await update.message.reply_text(f"Added expense: {description} (${amount}) to group '{group_name}'!")
