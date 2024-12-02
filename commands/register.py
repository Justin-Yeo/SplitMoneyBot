from telegram import Update
from telegram.ext import ContextTypes
from utils import load_data, save_data

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username

    data = load_data()
    if user_id not in data["users"]:
        data["users"][user_id] = {"username": username, "groups": []}
        save_data(data)
        await update.message.reply_text("You have been registered!")
    else:
        await update.message.reply_text("You are already registered.")
