from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.ext import ContextTypes

cancel_command = "cancel"

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Action cancelled.")
    return ConversationHandler.END