"""
debt_simplifier.py
==================
Minimizes the number of transactions needed to settle all debts within a group.

Algorithm: Directed-graph edge minimization via net-balance reduction.

Steps:
1.  Build a net-balance map: user_id → balance
      +  means the group owes them money (creditor)
      -  means they owe the group money (debtor)
2.  Use two heaps (max-heap by absolute value) to greedily match
    the largest debtor with the largest creditor.
3.  Emit one transaction per match; carry over any remainder.

Complexity: O(n log n) where n = number of non-zero balances.

Example
-------
    A owes B $10, B owes C $10
    Net balances: A → -10, B → 0, C → +10
    Result:       A pays C $10   (B is eliminated entirely)
"""

import heapq
from decimal import Decimal
from typing import Dict, List
from uuid import UUID

from app.schemas.expense import DebtSummary


def simplify_debts(balances: Dict[str, Decimal]) -> List[DebtSummary]:
    """
    Parameters
    ----------
    balances : Dict[str, Decimal]
        Mapping of user_id string → net balance.
        Positive = owed money by others; Negative = owes money.

    Returns
    -------
    List[DebtSummary]
        Minimal set of transactions that clear all balances.
    """
    ZERO = Decimal("0")
    PENNY = Decimal("0.01")

    # Separate into creditors (> 0) and debtors (< 0)
    # Use negative amounts for max-heap simulation via min-heap
    creditors: list = []   # (−amount, user_id)  → largest credit first
    debtors: list = []     # (−amount, user_id)  → largest debt first

    for uid, bal in balances.items():
        if bal > PENNY:
            heapq.heappush(creditors, (-bal, uid))
        elif bal < -PENNY:
            heapq.heappush(debtors, (bal, uid))    # already negative → min-heap = largest debt first

    transactions: List[DebtSummary] = []

    while creditors and debtors:
        # Largest creditor
        neg_credit, cred_uid = heapq.heappop(creditors)
        credit = -neg_credit

        # Largest debtor
        debt_val, debt_uid = heapq.heappop(debtors)
        debt = -debt_val  # make positive

        settled = min(credit, debt)

        transactions.append(
            DebtSummary(
                from_user_id=UUID(debt_uid),
                to_user_id=UUID(cred_uid),
                amount=settled,
            )
        )

        remaining_credit = credit - settled
        remaining_debt = debt - settled

        if remaining_credit > PENNY:
            heapq.heappush(creditors, (-remaining_credit, cred_uid))
        if remaining_debt > PENNY:
            heapq.heappush(debtors, (-remaining_debt, debt_uid))

    return transactions
