from telegram.ext import Application, CommandHandler
from commands.start import start
from commands.register import register
from commands.creategroup import create_group
from commands.addexpense import add_expense
from commands.viewbalances import view_balances


import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_API_KEY")

def main():
    # Initialize the bot application
    application = Application.builder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("creategroup", create_group))
    application.add_handler(CommandHandler("addexpense", add_expense))
    application.add_handler(CommandHandler("viewbalances", view_balances))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
