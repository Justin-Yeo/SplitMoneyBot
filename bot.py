from telegram.ext import Application, CommandHandler
from commands.start import start
from commands.register import register
from commands.creategroup import create_group
from commands.addexpense import add_expense
from commands.viewbalances import view_balances
from command.joingroup import join_group


import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_API_KEY")

def main():
    # Initialize the bot application
    application = Application.builder().token(TOKEN).build()

    # Register command handlers
    # first input to command handler is command we need to type eg. /creategroup
    # second input is the function to be called upon receivign the command
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("creategroup", create_group))
    application.add_handler(CommandHandler("addexpense", add_expense))
    application.add_handler(CommandHandler("viewbalances", view_balances))
    application.add_handler(CommandHandler("joingroup", join_group))


    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
