from telegram import Update
from telegram.ext import ContextTypes
from utils import load_data, save_data

join_group_command = "joingroup"

async def join_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /joingroup <group_name> <password>")
        return

    group_name = args[0]
    input_password = args[1]
    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username

    data = load_data()

    # Find the group by name
    group_id = next((gid for gid, g in data["groups"].items() if g["name"] == group_name), None)
    if not group_id:
        await update.message.reply_text("Group not found!")
        return

    # Check the password
    group_password = data["groups"][group_id]["password"]
    if group_password != input_password:
        await update.message.reply_text("Incorrect password! Please try again.")
        return

    # Check if the user is already a member
    if user_id in data["groups"][group_id]["members"]:
        await update.message.reply_text("You are already a member of this group!")
        return

    # Add the user to the group
    data["groups"][group_id]["members"].append(user_id)
    data["groups"][group_id]["balances"][user_id] = 0  # New members start with a balance of 0

    # Update the user's list of groups
    if user_id not in data["users"]:
        data["users"][user_id] = {"username": username, "groups": []}
    data["users"][user_id]["groups"].append(group_id)

    save_data(data)
    await update.message.reply_text(f"You have successfully joined the group '{group_name}'!")
