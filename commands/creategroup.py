from telegram import Update
from telegram.ext import ContextTypes
from utils import load_data, save_data

async def create_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args  # Get arguments passed with the command
    if not args:
        await update.message.reply_text("Usage: /create_group <group_name>")
        return

    group_name = " ".join(args)  # Combine arguments into a group name
    user_id = str(update.message.from_user.id)

    data = load_data()

    # Check if the group already exists
    for group in data["groups"].values():
        if group["name"] == group_name:
            await update.message.reply_text("A group with this name already exists!")
            return

    # Create the new group
    group_id = f"group{len(data['groups']) + 1}"
    data["groups"][group_id] = {
        "name": group_name,
        "members": [user_id],
        "expenses": [],
        "balances": {user_id: 0}
    }
    data["users"][user_id]["groups"].append(group_id)

    save_data(data)
    await update.message.reply_text(f"Group '{group_name}' created successfully!")
