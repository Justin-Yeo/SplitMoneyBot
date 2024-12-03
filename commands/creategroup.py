from telegram import Update
from telegram.ext import ContextTypes
from utils import load_data, save_data

create_group_command = "creategroup"

async def create_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        print(f"Arguments received: {args}")  # Debugging statement

        if len(args) < 2:
            await update.message.reply_text("Usage: /creategroup <group_name> <password>")
            return

        group_name = args[0]
        password = args[1]
        user_id = str(update.message.from_user.id)
        print(f"Creating group: {group_name} with password: {password}")  # Debugging statement

        data = load_data()
        print(f"Loaded data: {data}")  # Debugging statement

        # Check if the group already exists
        for group in data["groups"].values():
            if group["name"] == group_name:
                await update.message.reply_text("A group with this name already exists!")
                return

        # Create the new group
        group_id = f"group{len(data['groups']) + 1}"
        data["groups"][group_id] = {
            "name": group_name,
            "password": password,
            "members": [user_id],
            "expenses": [],
            "balances": {user_id: 0}
        }

        # Add group to the user's list of groups
        if user_id not in data["users"]:
            data["users"][user_id] = {"username": update.message.from_user.username, "groups": []}
        data["users"][user_id]["groups"].append(group_id)

        save_data(data)
        print(f"Group {group_name} created successfully!")  # Debugging statement
        await update.message.reply_text(f"Group '{group_name}' created successfully with a password!")

    except Exception as e:
        print(f"Error: {e}")  # Log any unexpected errors
        await update.message.reply_text("An error occurred while creating the group. Please try again.")
