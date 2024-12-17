from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from utils import load_data, save_data
from constants import ConvState  # Import the Enum for states

add_expense_command = "addexpense"

async def start_add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the add expense conversation."""
    chat_id = update.effective_chat.id

    # Get all users in the chat (group members)
    try:
        chat_members = await context.bot.get_chat_administrators(chat_id)
    except Exception as e:
        await update.message.reply_text("I could not retrieve the members of this group. Make sure I am an admin.")
        return ConversationHandler.END

    all_users = {str(member.user.id): member.user.username or member.user.first_name for member in chat_members}
    context.user_data['all_users'] = all_users

    keyboard = [[InlineKeyboardButton(username, callback_data=user_id)] for user_id, username in all_users.items()]
    keyboard.append([InlineKeyboardButton("Done", callback_data="done")])  # Add a "Done" button at the bottom
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.user_data['selected_users'] = set()  # Track selected users
    await update.message.reply_text("Select the users involved in the expense:", reply_markup=reply_markup)
    return ConvState.SELECT_USERS

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from constants import ConvState

async def select_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user selection from the Inline Keyboard."""
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    user_id = query.data

    # If the user clicks "Done"
    if user_id == "done":
        if not context.user_data.get('selected_users'):  # No users selected
            await query.edit_message_text(text="Please select at least one user.")
            return ConvState.SELECT_USERS

        # Move to selecting the payer
        context.user_data['payer'] = None  # Reset payer selection
        all_users = context.user_data['all_users']
        keyboard = [
            [InlineKeyboardButton(username, callback_data=user_id)]
            for user_id, username in all_users.items()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="Who paid for this expense? Select the payer:",
            reply_markup=reply_markup
        )
        return ConvState.SELECT_PAYER

    # Toggle user selection
    if 'selected_users' not in context.user_data:
        context.user_data['selected_users'] = set()

    if user_id in context.user_data['selected_users']:
        context.user_data['selected_users'].remove(user_id)
    else:
        context.user_data['selected_users'].add(user_id)

    # Update the keyboard
    all_users = context.user_data['all_users']
    keyboard = [
        [InlineKeyboardButton(f"✅ {username}" if user_id in context.user_data['selected_users'] else username, callback_data=user_id)]
        for user_id, username in all_users.items()
    ]
    keyboard.append([InlineKeyboardButton("Done", callback_data="done")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_reply_markup(reply_markup)
    return ConvState.SELECT_USERS

async def select_payer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payer selection."""
    query = update.callback_query
    await query.answer()

    # Store the selected payer
    context.user_data['payer'] = query.data

    # Get selected users and payer
    all_users = context.user_data['all_users']
    payer_name = all_users[query.data]
    selected_usernames = [username for user_id, username in all_users.items() if user_id in context.user_data['selected_users']]
    formatted_user_list = "\n".join([f"• {username}" for username in selected_usernames])

    # Send a confirmation message
    confirmation_keyboard = [
        [InlineKeyboardButton("✅ Confirm", callback_data="confirm")],
        [InlineKeyboardButton("🔄 Redo Selection", callback_data="redo")]
    ]
    reply_markup = InlineKeyboardMarkup(confirmation_keyboard)

    await query.message.reply_text(
        text=f"✅ **Expense Summary**:\n\n"
             f"Users involved:\n{formatted_user_list}\n\n"
             f"Payer: {payer_name}\n\n"
             f"Is this correct?",
        reply_markup=reply_markup
    )

    return ConvState.CONFIRM_SELECTION

async def enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"User input: {context.args}")  # Debug log to see what the input looks like

    if len(context.args) < 1:
        await update.message.reply_text("Please provide an amount. Example: /amount 50")
        return ConvState.ENTER_AMOUNT

    try:
        amount = float(context.args[0])  # Extract the amount from the command arguments
        if amount <= 0:
            await update.message.reply_text("Amount must be a positive number. Please try again.")
            return ConvState.ENTER_AMOUNT

        context.user_data["amount"] = amount
        await update.message.reply_text(f"Amount entered: ${amount}")
        await update.message.reply_text("Now input the name of this expense. Example: /reason food")
        return ConvState.ENTER_REASON
    except ValueError as e:
        print(f"Error converting input '{context.args[0]}' to float:", e)  # Debug log
        await update.message.reply_text("Invalid input. Please enter a valid number. Example: /amount 50")
        return ConvState.ENTER_AMOUNT

async def enter_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /reason command input."""
    print(f"User input for reason: {context.args}")  # Debug log to see what the input looks like

    if len(context.args) < 1:
        await update.message.reply_text("Please provide a reason for the expense. Example: /reason Dinner at McDonald's")
        return ConvState.ENTER_REASON

    # Join all the args to form the complete reason (in case the user enters multiple words)
    reason = " ".join(context.args)  # Join all args as a single reason
    context.user_data["reason"] = reason  # Save the reason to user_data

    await update.message.reply_text(f"Reason entered: {reason}. Expense has been recorded!")
    # Here you might want to finalize the expense or proceed to the next step
    return ConversationHandler.END

async def confirm_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirmation or redo."""
    query = update.callback_query
    await query.answer()

    if query.data == "confirm":
        await query.edit_message_text(text="Great! Please enter the amount of the expense.")
        return ConvState.ENTER_AMOUNT

    elif query.data == "redo":
        # Reset user and payer selection
        context.user_data['selected_users'] = set()
        context.user_data['payer'] = None

        all_users = context.user_data['all_users']
        keyboard = [
            [InlineKeyboardButton(username, callback_data=user_id)]
            for user_id, username in all_users.items()
        ]
        keyboard.append([InlineKeyboardButton("Done", callback_data="done")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="Select the users involved in the expense:",
            reply_markup=reply_markup
        )
        return ConvState.SELECT_USERS

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation."""
    await update.message.reply_text("Expense addition cancelled.")
    return ConversationHandler.END
