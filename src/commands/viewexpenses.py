from telegram import Update
from telegram.ext import ContextTypes
from utils import load_data

view_expenses_command = "viewexpenses"

async def view_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to display all expense details."""
    data = load_data()
    expenses = data.get("expenses", [])
    all_users = data.get("users", {})  # Load the user_id to username mapping

    if not expenses:
        await update.message.reply_text("No expenses recorded yet.")
        return

    # Format each expense for display
    result_message = "📜 *All Expense Details* 📜\n\n"
    for idx, expense in enumerate(expenses, start=1):
        payer_id = expense['payer']
        amount = expense['amount']
        reason = expense['reason']
        users_involved = expense['users_involved']

        # Convert user IDs to usernames
        payer_name = all_users.get(payer_id, f"User {payer_id}")
        involved_usernames = [all_users.get(user_id, f"User {user_id}") for user_id in users_involved]

        # Format for display
        result_message += (
            f"💰 *Expense {idx}*\n"
            f"- **Payer**: {payer_name}\n"
            f"- **Amount**: ${amount:.2f}\n"
            f"- **Reason**: {reason}\n"
            f"- **Involved**: {', '.join(involved_usernames)}\n"
            f"---------------------------\n"
        )

    await update.message.reply_text(result_message, parse_mode="Markdown")
