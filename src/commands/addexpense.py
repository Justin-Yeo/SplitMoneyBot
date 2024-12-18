from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from utils import load_data, save_data
from constants import ConvState  

add_expense_command = "addexpense"

async def start_add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def select_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  

    user_id = query.data

    if user_id == "done":
        if not context.user_data.get('selected_users'):  
            await query.edit_message_text(text="Please select at least one user.")
            return ConvState.SELECT_USERS

        # Move to selecting the payer
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
    query = update.callback_query
    await query.answer()

    # Store the selected payer
    context.user_data['payer'] = query.data
    payer_name = context.user_data['all_users'][query.data]

    await query.edit_message_text(
        text=f"Payer selected: {payer_name}. Now enter the amount of the expense. Example: /amount 50"
    )

    return ConvState.ENTER_AMOUNT

async def enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    if len(context.args) < 1:
        await update.message.reply_text("Please provide a reason for the expense. Example: /reason fried chicken dinner")
        return ConvState.ENTER_REASON

    reason = " ".join(context.args) 
    context.user_data["reason"] = reason 

    # Extract data from user_data
    data = load_data()
    users_involved = list(context.user_data['selected_users'])
    payer_id = context.user_data['payer']
    amount = context.user_data['amount']
    reason = context.user_data['reason']
    all_users = context.user_data['all_users']

    # Add the expense to the data file
    expense = {
        "users_involved": users_involved,
        "payer": payer_id,
        "amount": amount,
        "reason": reason
    }
    data["expenses"].append(expense)
    save_data(data)

    # Format a summary message
    selected_usernames = [all_users[user_id] for user_id in users_involved]
    payer_name = all_users[payer_id]

    summary = (
        f"✅ Expense Recorded:\n"
        f"- Users involved: {', '.join(selected_usernames)}\n"
        f"- Payer: {payer_name}\n"
        f"- Amount: ${amount:.2f}\n"
        f"- Reason: {reason}"
    )

    await update.message.reply_text(summary)

    # End the conversation
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Expense addition cancelled.")
    return ConversationHandler.END
