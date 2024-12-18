from telegram import Update
from telegram.ext import ContextTypes
from utils import load_data, save_data

sync_users_command = "sync"

async def sync_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("sync function called")
    chat_id = update.effective_chat.id

    try:
        # Get all admins in the chat
        chat_members = await context.bot.get_chat_administrators(chat_id)
    except Exception as e:
        await update.message.reply_text("Unable to sync users. Ensure I am an admin in this group.")
        return

    # Load existing users from data.json
    data = load_data()
    users = data.get("users", {})

    # Add/update users from chat members
    for member in chat_members:
        user_id = str(member.user.id)
        username = member.user.username or member.user.first_name  # Use username if available, else use first name
        users[user_id] = username

    # Save updated users to data.json
    data["users"] = users
    save_data(data)

    await update.message.reply_text("User list has been successfully updated! 🎉\n\n" + 
                                    f"Total users synced: {len(users)}\n" + 
                                    f"Users: {', '.join(users.values())}")
