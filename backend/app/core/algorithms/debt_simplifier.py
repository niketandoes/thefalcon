from typing import List, Dict, TypedDict
from decimal import Decimal
from uuid import UUID
from app.schemas.expense import DebtSummary

class DebtNode(TypedDict):
    user_id: str
    amount: Decimal

def simplify_debts(balances: Dict[str, Decimal]) -> List[DebtSummary]:
    """
    Given a dictionary of user_id -> net_balance (positive means they are owed money,
    negative means they owe money), calculate the minimum transactions to settle debts
    using a simple greedy algorithm.
    """
    debtors: List[DebtNode] = []   # Users who owe money (negative balance)
    creditors: List[DebtNode] = [] # Users who are owed money (positive balance)

    for uid, balance in balances.items():
        if balance < Decimal("0"):
            debtors.append({'user_id': uid, 'amount': abs(balance)})
        elif balance > Decimal("0"):
            creditors.append({'user_id': uid, 'amount': balance})

    # Sort debtors and creditors descending by amount to minimize transactions implicitly
    debtors.sort(key=lambda x: x['amount'], reverse=True)
    creditors.sort(key=lambda x: x['amount'], reverse=True)

    transactions: List[DebtSummary] = []
    i, j = 0, 0

    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]

        settled_amount = min(debtor['amount'], creditor['amount'])

        transactions.append(DebtSummary(
            from_user_id=UUID(debtor['user_id']),
            to_user_id=UUID(creditor['user_id']),
            amount=settled_amount
        ))

        debtor['amount'] -= settled_amount
        creditor['amount'] -= settled_amount

        if debtor['amount'] == Decimal("0"):
            i += 1
        if creditor['amount'] == Decimal("0"):
            j += 1

    return transactions
