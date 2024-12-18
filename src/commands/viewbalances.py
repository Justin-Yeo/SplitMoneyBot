from telegram import Update
from telegram.ext import ContextTypes
from utils import load_data
from collections import defaultdict

view_balances_command = "viewbalances"

async def view_balances(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    expenses = data.get("expenses", [])
    all_users = data.get("users", {})  

    transactions = []
    for expense in expenses:
        payer = expense['payer']
        amount = expense['amount']
        users_involved = expense['users_involved']

        transactions.append((payer, payer, amount))  

        split_amount = amount / len(users_involved) 
        for user in users_involved:
            transactions.append((user, payer, split_amount))  

    results = min_cash_flow(transactions, all_users)

    if not results:
        await update.message.reply_text("No transactions to settle. Balances are already even.")
        return

    result_message = "💸 *Settlement Summary* 💸\n\n"
    for line in results:
        result_message += f"{line}\n"

    await update.message.reply_text(result_message, parse_mode="Markdown")
    
def min_cash_flow(transactions, user_map):
    balance = defaultdict(int)
    for payer, payee, amount in transactions:
        balance[payer] -= amount
        balance[payee] += amount

    debtors = []
    creditors = []
    for user, amount in balance.items():
        if amount < 0:
            debtors.append((user, amount))  
        elif amount > 0:
            creditors.append((user, amount)) 

    transactions_result = []

    def settle_debts(debtors, creditors):
        if not debtors or not creditors:
            return

        debtor, debt_amount = debtors.pop()
        creditor, credit_amount = creditors.pop()
        settlement = min(-debt_amount, credit_amount)

        debtor_name = user_map.get(debtor, debtor)
        creditor_name = user_map.get(creditor, creditor)
        transactions_result.append(f"{debtor_name} pays {creditor_name} ${settlement:.2f}")

        settle_debts(debtors, creditors)

    settle_debts(debtors, creditors)
    return transactions_result
