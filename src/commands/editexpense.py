from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from utils import load_data, save_data
from constants import ConvState  # Import the Enum class for conversation states

edit_expense_command = "editexpense"

async def start_edit_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    expenses = data.get("expenses", [])

    if not expenses:
        await update.message.reply_text("No expenses available to edit.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton(f"Expense {idx+1}: {expense['reason']} (${expense['amount']})", callback_data=str(idx))]
        for idx, expense in enumerate(expenses)
    ]
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Select an expense to edit:", reply_markup=reply_markup)
    return ConvState.SELECT_EXPENSE

async def select_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    
    if query.data == "cancel":
        await query.edit_message_text(text="Editing process cancelled.")
        return ConversationHandler.END

    selected_expense_index = int(query.data)
    context.user_data['selected_expense_index'] = selected_expense_index
    expense = data['expenses'][selected_expense_index]

    keyboard = [
        [InlineKeyboardButton("Edit Payer", callback_data="edit_payer")],
        [InlineKeyboardButton("Edit Users Involved", callback_data="edit_users")],
        [InlineKeyboardButton("Edit Amount", callback_data="edit_amount")],
        [InlineKeyboardButton("Edit Reason", callback_data="edit_reason")],
        [InlineKeyboardButton("Delete Expense", callback_data="delete")],
        [InlineKeyboardButton("Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    all_users = data.get('users', {})
    usernames = [all_users.get(user_id, 'Unknown User') for user_id in expense['users_involved']]
    payer_name = all_users.get(expense['payer'], 'Unknown User')

    await query.edit_message_text(
    text=(
        f"Selected Expense:\n"
        f"- **Payer**: {payer_name}\n"
        f"- **Amount**: ${expense['amount']:.2f}\n"
        f"- **Reason**: {expense['reason']}\n"
        f"- **Users**: {', '.join(usernames)}"
    ),
    parse_mode="Markdown",
    reply_markup=reply_markup
    )

    return ConvState.EDIT_OPTION

async def handle_edit_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text(text="Editing process cancelled.")
        return ConversationHandler.END

    context.user_data['edit_field'] = query.data

    if query.data == 'edit_payer':
        data = load_data()
        all_users = data.get("users", {})
        keyboard = [
            [InlineKeyboardButton(username, callback_data=user_id)]
            for user_id, username in all_users.items()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Select a new payer:", reply_markup=reply_markup)
        return ConvState.SELECT_PAYER_NEW

    if query.data == 'edit_users':
        data = load_data()
        all_users = data.get("users", {})

        expense_index = context.user_data.get('selected_expense_index')

        if expense_index is None or not (0 <= expense_index < len(data.get('expenses', []))):
            await query.edit_message_text(text="No valid expense was selected.")
            return ConversationHandler.END
        
        expense = data['expenses'][expense_index]
        if 'selected_users' not in context.user_data:
            context.user_data['selected_users'] = set(expense.get('users_involved', []))

        keyboard = [
        [InlineKeyboardButton(f"✅ {username}" if user_id in context.user_data['selected_users'] else username, callback_data=user_id)]
        for user_id, username in all_users.items()
        ]
        keyboard.append([InlineKeyboardButton("Done", callback_data="done")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Select new users involved:", reply_markup=reply_markup)
        return ConvState.SELECT_USERS_NEW
    
    if query.data == 'edit_amount':
        await query.edit_message_text(text="Please enter the new value using /amount <value>. Example: /amount 500")
        return ConvState.EDIT_AMOUNT

    if query.data == 'edit_reason':
        await query.edit_message_text(text="Please enter the new value using /reason <reason>. Example: /reason lunch")
        return ConvState.EDIT_REASON
    
    if query.data == "delete":
        # Load data and get the selected expense index
        data = load_data()
        expense_index = context.user_data.get('selected_expense_index')

        # Check if expense_index is valid
        if expense_index is None or not (0 <= expense_index < len(data.get('expenses', []))):
            await query.edit_message_text(text="No valid expense was selected.")
            return ConversationHandler.END

        # Get the details of the expense before deletion
        deleted_expense = data['expenses'][expense_index]

        # Extract expense details
        payer = data['users'].get(deleted_expense['payer'], 'Unknown User')
        amount = deleted_expense.get('amount', 0)
        reason = deleted_expense.get('reason', 'No reason provided')
        users_involved = [data['users'].get(user_id, 'Unknown User') for user_id in deleted_expense.get('users_involved', [])]

        # Remove the expense from the data
        del data['expenses'][expense_index]
        save_data(data)

        # Format the message with the details of the deleted expense
        deleted_expense_message = (
            f"🗑️ *Expense Deleted!*\n\n"
            f"**Payer**: {payer}\n"
            f"**Amount**: ${amount:.2f}\n"
            f"**Reason**: {reason}\n"
            f"**Users Involved**: {', '.join(users_involved) if users_involved else 'No users involved'}"
        )

        await query.edit_message_text(text=deleted_expense_message, parse_mode="Markdown")
        return ConversationHandler.END

async def select_new_payer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_user_id = query.data
    expense_index = context.user_data.get('selected_expense_index')

    data = load_data()
    expense = data['expenses'][expense_index]
    expense['payer'] = selected_user_id

    save_data(data)
    await query.edit_message_text(text="Payer successfully updated! 🎉")
    return ConversationHandler.END

async def select_new_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Select new users involved in the expense (similar to select_users)."""
    query = update.callback_query
    await query.answer()

    user_id = query.data
    expense_index = context.user_data.get('selected_expense_index')

    data = load_data()
    expense = data['expenses'][expense_index]

    # If 'done' is clicked, finalize selection and save the changes
    if user_id == "done":
        if not context.user_data.get('selected_users'):  
            await query.edit_message_text(text="You have not selected any users. If you would like to delete use the delete option, if not try again and select at least one user.")
            return ConversationHandler.END;

        # Update the expense's 'users_involved' list
        expense['users_involved'] = list(context.user_data['selected_users'])
        save_data(data)

        selected_usernames = [data['users'].get(user_id, 'Unknown User') for user_id in expense['users_involved']]
        await query.edit_message_text(text=f"People involved successfully updated! 🎉 Involved: {', '.join(selected_usernames)}")
        return ConversationHandler.END

    # Initialize the 'selected_users' from the context user_data
    if 'selected_users' not in context.user_data:
        context.user_data['selected_users'] = set(expense.get('users_involved', []))  # Initialize with users already involved

    # Toggle user selection (like a checkbox)
    if user_id != "done":
        if user_id in context.user_data['selected_users']:
            context.user_data['selected_users'].remove(user_id)
        else:
            context.user_data['selected_users'].add(user_id)

    # Update the inline keyboard to show selected users
    all_users = data['users']
    keyboard = [
        [InlineKeyboardButton(f"✅ {username}" if user_id in context.user_data['selected_users'] else username, callback_data=user_id)] 
        for user_id, username in all_users.items()
    ]
    keyboard.append([InlineKeyboardButton("Done", callback_data="done")])  # Add a "Done" button at the bottom
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_reply_markup(reply_markup)
    return ConvState.SELECT_USERS_NEW

async def update_expense_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    field_to_edit = context.user_data.get('edit_field')
    expense_index = context.user_data.get('selected_expense_index')

    data = load_data()
    expense = data['expenses'][expense_index]

    if field_to_edit == 'edit_amount' and user_input.startswith('/amount'):
        if len(user_input.split(' ', 1)) < 2:
            await update.message.reply_text("Please provide an amount. Use /amount <value>.")
            return ConvState.EDIT_FIELD

        _, amount = user_input.split(' ', 1)
        try:
            amount = float(amount)
            if amount <= 0:
                await update.message.reply_text("Amount must be a positive number. Please try again using /amount <value>.")
                return ConvState.EDIT_FIELD

            expense['amount'] = amount
            await update.message.reply_text(f"Amount updated successfully to ${amount:.2f} 🎉")
        except ValueError:
            await update.message.reply_text("Invalid amount. Please enter a valid number using /amount <value>.")
            return ConvState.EDIT_FIELD

    else:
        await update.message.reply_text(
            "Invalid input. Please use:\n"
            "- /amount <value> to update the amount\n"
        )
        return ConvState.EDIT_FIELD

    # Save updated data
    save_data(data)
    return ConversationHandler.END

async def update_expense_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    field_to_edit = context.user_data.get('edit_field')
    expense_index = context.user_data.get('selected_expense_index')

    data = load_data()
    expense = data['expenses'][expense_index]

    if field_to_edit == 'edit_reason' and user_input.startswith('/reason'):
        if len(user_input.split(' ', 1)) < 2:
            await update.message.reply_text("Please provide a reason. Use /reason <value>.")
            return ConvState.EDIT_FIELD

        _, reason = user_input.split(' ', 1)
        expense['reason'] = reason.strip()
        await update.message.reply_text(f"Reason updated successfully to '{reason.strip()}' 🎉")

    else:
        await update.message.reply_text(
            "Invalid input. Please use:\n"
            "- /reason <value> to update the reason\n"
        )
        return ConvState.EDIT_FIELD

    # Save updated data
    save_data(data)
    return ConversationHandler.END

