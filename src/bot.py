from telegram.ext import Application, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from commands.start import start, start_command
from commands.addexpense import start_add_expense, select_users, select_payer, enter_amount, enter_reason, cancel, add_expense_command
from commands.viewbalances import view_balances, view_balances_command
from commands.syncusers import sync_users, sync_users_command
from utils import load_data
from constants import ConvState  # Import the Enum class for conversation states

import os
from dotenv import load_dotenv

# Load environment variables (like TELEGRAM_API_KEY)
load_dotenv()
TOKEN = os.getenv("TELEGRAM_API_KEY")
data = load_data()

def main():
    # Initialize the bot application
    application = Application.builder().token(TOKEN).build()

    # Register simple command handlers
    application.add_handler(CommandHandler(start_command, start))  # /start command
    application.add_handler(CommandHandler(view_balances_command, view_balances))  # /viewbalances command
    application.add_handler(CommandHandler(sync_users_command, sync_users))

    # Register the add_expense conversation handler (for multi-step conversation)
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler(add_expense_command, start_add_expense)],  # User types /addexpense
        states={
            ConvState.SELECT_USERS: [CallbackQueryHandler(select_users)],  # Step 1: Select the users involved
            ConvState.SELECT_PAYER: [CallbackQueryHandler(select_payer)],  # Step 2: Select the user who paid
            ConvState.ENTER_AMOUNT: [CommandHandler('amount', enter_amount)], 
            ConvState.ENTER_REASON: [CommandHandler('reason', enter_reason)], 
        },
        fallbacks=[CommandHandler("cancel", cancel)]  # Handles the /cancel command
    ))

    # Start the bot (polling for updates)
    application.run_polling()

if __name__ == "__main__":
    main()
