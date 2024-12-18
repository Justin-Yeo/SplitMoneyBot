from telegram.ext import Application, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from commands.start import start, start_command
from commands.addexpense import start_add_expense, select_users, select_payer, enter_amount, enter_reason, cancel, add_expense_command
from commands.settle import settle, settle_command
from commands.syncusers import sync_users, sync_users_command
from commands.viewexpenses import view_expenses, view_expenses_command
from commands.editexpense import start_edit_expense, select_expense, handle_edit_option, select_new_payer, select_new_users, update_expense_amount, update_expense_reason
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
    application.add_handler(CommandHandler(start_command, start))  
    application.add_handler(CommandHandler(settle_command, settle))  
    application.add_handler(CommandHandler(sync_users_command, sync_users))
    application.add_handler(CommandHandler(view_expenses_command, view_expenses))

    # Register the add_expense conversation handler (for multi-step conversation)
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler(add_expense_command, start_add_expense)],  
        states={
            ConvState.SELECT_USERS: [CallbackQueryHandler(select_users)],  
            ConvState.SELECT_PAYER: [CallbackQueryHandler(select_payer)],  
            ConvState.ENTER_AMOUNT: [CommandHandler('amount', enter_amount)], 
            ConvState.ENTER_REASON: [CommandHandler('reason', enter_reason)], 
        },
        fallbacks=[CommandHandler("cancel", cancel)]  
    ))

    application.add_handler(ConversationHandler(
    entry_points=[CommandHandler("editexpense", start_edit_expense)],
    states={
        ConvState.SELECT_EXPENSE: [CallbackQueryHandler(select_expense)],
        ConvState.EDIT_OPTION: [CallbackQueryHandler(handle_edit_option)],
        ConvState.SELECT_PAYER_NEW: [CallbackQueryHandler(select_new_payer)],  # Handles payer selection
        ConvState.SELECT_USERS_NEW: [CallbackQueryHandler(select_new_users)],  # Handles user selection
        ConvState.EDIT_AMOUNT: [CommandHandler('amount', update_expense_amount)],  # Handles text-based edits
        ConvState.EDIT_REASON: [CommandHandler('reason', update_expense_reason)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]  # Handles the /cancel command
    ))

    # Start the bot (polling for updates)
    application.run_polling()

if __name__ == "__main__":
    main()
