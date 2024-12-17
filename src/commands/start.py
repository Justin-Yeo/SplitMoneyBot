from telegram import Update
from telegram.ext import ContextTypes

start_command = "start"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to your Splitwise Bot!")
