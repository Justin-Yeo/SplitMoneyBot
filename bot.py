from telegram.ext import Application, CommandHandler
from commands.start import start, start_command
from commands.register import register, register_command
from commands.creategroup import create_group, create_group_command
from commands.addexpense import add_expense, add_expense_command
from commands.viewbalances import view_balances, view_balances_command
from commands.joingroup import join_group, join_group_command

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
    application.add_handler(CommandHandler(start_command, start))
    application.add_handler(CommandHandler(register_command, register))
    application.add_handler(CommandHandler(create_group_command, create_group))
    application.add_handler(CommandHandler(add_expense_command, add_expense))
    application.add_handler(CommandHandler(view_balances_command, view_balances))
    application.add_handler(CommandHandler(join_group_command, join_group))


    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
