"""
expense_splitter.py
====================
Core expense calculation engine for splitting a single logged expense
among users via four distinct methods.

Split Methods
-------------
1. Equal       – divide total evenly among all participants
2. Percentage  – each user owns a declared % of the total (must sum to 100)
3. Share-based – proportional split driven by share counts (e.g. 2:1)
4. Exact       – each user declares their exact owed amount (must sum to total)

Penny-correction guarantee
--------------------------
All methods use a "largest-remainder" (Hamilton) approach so the sum of
every rounded result is *exactly* equal to the original total_amount.
Any rounding residual (the infamous "penny") is assigned to / removed from
the user with the largest fractional remainder, with ties broken by the
insertion order of the input collection.

Dependencies
------------
Standard library only (Python >= 3.10).  No third-party packages required.
Pydantic-compatible type annotations are used throughout for drop-in
compatibility if you later choose to wrap these functions in Pydantic schemas.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Dict, List


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _to_decimal(value: float | int | Decimal | str) -> Decimal:
    """Losslessly convert any numeric type to Decimal (avoids float imprecision)."""
    return Decimal(str(value))


def _largest_remainder_round(
    raw_shares: Dict[str, Decimal],
    total: Decimal,
) -> Dict[str, Decimal]:
    """
    Distribute *total* across user IDs so that:
      • every individual value is rounded to exactly 2 d.p.
      • the sum of all values equals *total* exactly.

    Uses the largest-remainder (Hamilton) method:
      1. Floor each value to 2 d.p. (never round up in the first pass).
      2. Compute how many pennies are still unallocated.
      3. Award one extra penny to the user(s) with the largest fractional
         remainder that was lost during flooring.  Ties are broken by the
         insertion order of *raw_shares* (first user wins).

    Parameters
    ----------
    raw_shares : Dict[str, Decimal]
        Mapping of user_id -> un-rounded owed amount.
    total : Decimal
        The authoritative total that rounded outputs must sum to exactly.

    Returns
    -------
    Dict[str, Decimal]
        user_id -> final rounded owed amount (2 d.p.), preserving order.
    """
    penny = Decimal("0.01")
    floored: Dict[str, Decimal] = {}
    remainders: Dict[str, Decimal] = {}

    for uid, amount in raw_shares.items():
        # Truncate to 2 d.p. without rounding up (ROUND_FLOOR on scaled value)
        floored_val = (amount * 100).to_integral_value(
            rounding="ROUND_FLOOR"
        ) / 100
        floored[uid] = floored_val
        remainders[uid] = amount - floored_val

    current_sum = sum(floored.values(), Decimal("0.00"))
    # Signed penny count: positive = we need to give more, negative = took too much
    delta_pennies = int(round((total - current_sum) / penny))

    if delta_pennies > 0:
        # Sort by remainder descending; for ties, preserve original insertion order
        sorted_uids = sorted(
            raw_shares.keys(),
            key=lambda uid: remainders[uid],
            reverse=True,
        )
        for uid in sorted_uids[:delta_pennies]:
            floored[uid] += penny

    elif delta_pennies < 0:
        # Reclaim pennies from users with the *smallest* remainders first
        sorted_uids = sorted(
            raw_shares.keys(),
            key=lambda uid: remainders[uid],
        )
        for uid in sorted_uids[: abs(delta_pennies)]:
            floored[uid] -= penny

    return floored


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _require_positive_total(total: Decimal) -> None:
    if total <= 0:
        raise ValueError(
            f"total_amount must be greater than zero (got {total})."
        )


def _require_non_empty_dict(d: dict, label: str) -> None:
    if not d:
        raise ValueError(f"{label} must not be empty.")


def _require_non_empty_list(lst: list, label: str) -> None:
    if not lst:
        raise ValueError(f"{label} must contain at least one user.")


def _require_no_duplicates(lst: List[str], label: str) -> None:
    if len(lst) != len(set(lst)):
        raise ValueError(f"{label} must not contain duplicate user IDs.")


# ---------------------------------------------------------------------------
# Input schemas (plain dataclasses – swap for Pydantic BaseModel if desired)
# ---------------------------------------------------------------------------

@dataclass
class EqualSplitInput:
    total_amount: Decimal
    user_ids: List[str]

    def __post_init__(self) -> None:
        _require_positive_total(self.total_amount)
        _require_non_empty_list(self.user_ids, "user_ids")
        _require_no_duplicates(self.user_ids, "user_ids")


@dataclass
class PercentageSplitInput:
    total_amount: Decimal
    user_percentages: Dict[str, Decimal]

    def __post_init__(self) -> None:
        _require_positive_total(self.total_amount)
        _require_non_empty_dict(self.user_percentages, "user_percentages")
        for uid, pct in self.user_percentages.items():
            if pct < 0:
                raise ValueError(
                    f"Percentage for '{uid}' must not be negative (got {pct})."
                )
        total_pct = sum(self.user_percentages.values(), Decimal("0"))
        if abs(total_pct - Decimal("100")) > Decimal("0.0001"):
            raise ValueError(
                f"Percentages must sum to exactly 100 (got {total_pct})."
            )


@dataclass
class ShareSplitInput:
    total_amount: Decimal
    user_shares: Dict[str, Decimal]

    def __post_init__(self) -> None:
        _require_positive_total(self.total_amount)
        _require_non_empty_dict(self.user_shares, "user_shares")
        for uid, shares in self.user_shares.items():
            if shares <= 0:
                raise ValueError(
                    f"Shares for '{uid}' must be greater than zero (got {shares})."
                )


@dataclass
class ExactSplitInput:
    total_amount: Decimal
    user_exact_amounts: Dict[str, Decimal]

    def __post_init__(self) -> None:
        _require_positive_total(self.total_amount)
        _require_non_empty_dict(self.user_exact_amounts, "user_exact_amounts")
        for uid, amount in self.user_exact_amounts.items():
            if amount < 0:
                raise ValueError(
                    f"Exact amount for '{uid}' must not be negative (got {amount})."
                )
        declared_sum = sum(self.user_exact_amounts.values(), Decimal("0"))
        if abs(declared_sum - self.total_amount) > Decimal("0.0001"):
            raise ValueError(
                f"Sum of exact amounts ({declared_sum}) does not match "
                f"total_amount ({self.total_amount})."
            )


# ---------------------------------------------------------------------------
# Public API — four split calculators
# ---------------------------------------------------------------------------

def split_equal(
    total_amount: float | Decimal,
    user_ids: List[str],
) -> Dict[str, Decimal]:
    """
    Divide *total_amount* equally among *user_ids*.

    Any unallocated penny is awarded to the user with the largest fractional
    remainder; for equal splits (where all remainders are identical) this
    means the *first* user in the list absorbs it.

    Parameters
    ----------
    total_amount : float | Decimal
        The full expense amount to be split.
    user_ids : List[str]
        Ordered list of participant IDs. Must be non-empty, no duplicates.

    Returns
    -------
    Dict[str, Decimal]
        user_id -> owed amount (2 d.p.), summing *exactly* to total_amount.

    Raises
    ------
    ValueError
        If user_ids is empty / contains duplicates, or total_amount <= 0.

    Examples
    --------
    >>> split_equal(10.00, ["alice", "bob", "charlie"])
    {'alice': Decimal('3.34'), 'bob': Decimal('3.33'), 'charlie': Decimal('3.33')}
    """
    inp = EqualSplitInput(
        total_amount=_to_decimal(total_amount),
        user_ids=list(user_ids),
    )
    total = inp.total_amount
    n = Decimal(len(inp.user_ids))
    raw_share = total / n
    raw_shares = {uid: raw_share for uid in inp.user_ids}
    return _largest_remainder_round(raw_shares, total)


def split_percentage(
    total_amount: float | Decimal,
    user_percentages: Dict[str, float | Decimal],
) -> Dict[str, Decimal]:
    """
    Allocate *total_amount* according to declared percentages.

    Parameters
    ----------
    total_amount : float | Decimal
        The full expense amount to be split.
    user_percentages : Dict[str, float | Decimal]
        Mapping of user_id -> percentage (0-100). Must sum to exactly 100.

    Returns
    -------
    Dict[str, Decimal]
        user_id -> owed amount (2 d.p.), summing *exactly* to total_amount.

    Raises
    ------
    ValueError
        If percentages don't sum to 100, contain negatives, or total <= 0.

    Examples
    --------
    >>> split_percentage(200.00, {"alice": 70, "bob": 30})
    {'alice': Decimal('140.00'), 'bob': Decimal('60.00')}
    """
    inp = PercentageSplitInput(
        total_amount=_to_decimal(total_amount),
        user_percentages={k: _to_decimal(v) for k, v in user_percentages.items()},
    )
    total = inp.total_amount
    raw_shares = {
        uid: (pct / Decimal("100")) * total
        for uid, pct in inp.user_percentages.items()
    }
    return _largest_remainder_round(raw_shares, total)


def split_shares(
    total_amount: float | Decimal,
    user_shares: Dict[str, float | Decimal],
) -> Dict[str, Decimal]:
    """
    Distribute *total_amount* proportionally by share count.

    Parameters
    ----------
    total_amount : float | Decimal
        The full expense amount to be split.
    user_shares : Dict[str, float | Decimal]
        Mapping of user_id -> number of shares (must be > 0).

    Returns
    -------
    Dict[str, Decimal]
        user_id -> owed amount (2 d.p.), summing *exactly* to total_amount.

    Raises
    ------
    ValueError
        If any share value is <= 0, or total_amount <= 0.

    Examples
    --------
    >>> split_shares(90.00, {"alice": 2, "bob": 1})
    {'alice': Decimal('60.00'), 'bob': Decimal('30.00')}
    """
    inp = ShareSplitInput(
        total_amount=_to_decimal(total_amount),
        user_shares={k: _to_decimal(v) for k, v in user_shares.items()},
    )
    total = inp.total_amount
    total_shares = sum(inp.user_shares.values(), Decimal("0"))
    raw_shares = {
        uid: (shares / total_shares) * total
        for uid, shares in inp.user_shares.items()
    }
    return _largest_remainder_round(raw_shares, total)


def split_exact(
    total_amount: float | Decimal,
    user_exact_amounts: Dict[str, float | Decimal],
) -> Dict[str, Decimal]:
    """
    Accept user-declared exact amounts (item-level split).

    Validates the declared amounts match the total, then returns them
    rounded to exactly 2 d.p. with penny-correction applied if needed.

    Parameters
    ----------
    total_amount : float | Decimal
        The authoritative expense total.
    user_exact_amounts : Dict[str, float | Decimal]
        Mapping of user_id -> the exact amount they owe.

    Returns
    -------
    Dict[str, Decimal]
        user_id -> owed amount (2 d.p.), summing *exactly* to total_amount.

    Raises
    ------
    ValueError
        If declared amounts don't sum to total, any amount < 0,
        or total_amount <= 0.

    Examples
    --------
    >>> split_exact(100.00, {"alice": 60.00, "bob": 40.00})
    {'alice': Decimal('60.00'), 'bob': Decimal('40.00')}
    """
    inp = ExactSplitInput(
        total_amount=_to_decimal(total_amount),
        user_exact_amounts={k: _to_decimal(v) for k, v in user_exact_amounts.items()},
    )
    return _largest_remainder_round(inp.user_exact_amounts, inp.total_amount)


# ---------------------------------------------------------------------------
# Unified entry-point dispatcher
# ---------------------------------------------------------------------------

class SplitMethod(str, Enum):
    EQUAL      = "equal"
    PERCENTAGE = "percentage"
    SHARES     = "shares"
    EXACT      = "exact"


def calculate_debt_distribution(
    method: SplitMethod | str,
    total_amount: float | Decimal,
    *,
    user_ids: List[str] | None = None,
    user_percentages: Dict[str, float | Decimal] | None = None,
    user_shares: Dict[str, float | Decimal] | None = None,
    user_exact_amounts: Dict[str, float | Decimal] | None = None,
) -> Dict[str, Decimal]:
    """
    Unified dispatcher — pick a split method and supply the matching kwarg.

    Parameters
    ----------
    method : SplitMethod | str
        "equal" | "percentage" | "shares" | "exact"
    total_amount : float | Decimal
        Full expense amount.
    user_ids : List[str], optional
        Required for method=EQUAL.
    user_percentages : Dict[str, float | Decimal], optional
        Required for method=PERCENTAGE.
    user_shares : Dict[str, float | Decimal], optional
        Required for method=SHARES.
    user_exact_amounts : Dict[str, float | Decimal], optional
        Required for method=EXACT.

    Returns
    -------
    Dict[str, Decimal]
        user_id -> final owed amount rounded to 2 d.p.

    Raises
    ------
    ValueError
        On validation failure or a missing required parameter.
    """
    try:
        method = SplitMethod(method)
    except ValueError:
        valid = [m.value for m in SplitMethod]
        raise ValueError(
            f"Unknown split method '{method}'. Valid options: {valid}."
        )

    match method:
        case SplitMethod.EQUAL:
            if user_ids is None:
                raise ValueError("user_ids is required for the EQUAL split method.")
            return split_equal(total_amount, user_ids)

        case SplitMethod.PERCENTAGE:
            if user_percentages is None:
                raise ValueError(
                    "user_percentages is required for the PERCENTAGE split method."
                )
            return split_percentage(total_amount, user_percentages)

        case SplitMethod.SHARES:
            if user_shares is None:
                raise ValueError(
                    "user_shares is required for the SHARES split method."
                )
            return split_shares(total_amount, user_shares)

        case SplitMethod.EXACT:
            if user_exact_amounts is None:
                raise ValueError(
                    "user_exact_amounts is required for the EXACT split method."
                )
            return split_exact(total_amount, user_exact_amounts)


# ---------------------------------------------------------------------------
# Self-contained test suite — run with:  python expense_splitter.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    D = Decimal
    results = {"passed": 0, "failed": 0}

    GREEN = "\033[92m"
    RED   = "\033[91m"
    RESET = "\033[0m"
    BOLD  = "\033[1m"
    DIM   = "\033[2m"

    def check(label: str, result, expected) -> None:
        ok = result == expected
        icon = f"{GREEN}✓ PASS{RESET}" if ok else f"{RED}✗ FAIL{RESET}"
        results["passed" if ok else "failed"] += 1
        print(f"  {icon}  {label}")
        if not ok:
            print(f"{DIM}       Expected : {expected}")
            print(f"       Got      : {result}{RESET}")

    def expect_error(label: str, fn, *args, **kwargs) -> None:
        try:
            fn(*args, **kwargs)
            print(f"  {RED}✗ FAIL{RESET}  {label}  (no ValueError raised!)")
            results["failed"] += 1
        except ValueError as exc:
            print(f"  {GREEN}✓ PASS{RESET}  {label}")
            print(f"  {DIM}         ↳ {exc}{RESET}")
            results["passed"] += 1

    # ── Equal Split ───────────────────────────────────────────────────────
    print(f"\n{BOLD}━━━  1. Equal Split  ━━━{RESET}")

    check(
        "Classic penny problem: 10.00 ÷ 3 → [3.34, 3.33, 3.33]",
        split_equal(10.00, ["alice", "bob", "charlie"]),
        {"alice": D("3.34"), "bob": D("3.33"), "charlie": D("3.33")},
    )
    check(
        "Exact division: 9.00 ÷ 3 → [3.00, 3.00, 3.00]",
        split_equal(9.00, ["alice", "bob", "charlie"]),
        {"alice": D("3.00"), "bob": D("3.00"), "charlie": D("3.00")},
    )
    check(
        "Tiny amounts: 0.10 ÷ 3 → [0.04, 0.03, 0.03]",
        split_equal(0.10, ["u1", "u2", "u3"]),
        {"u1": D("0.04"), "u2": D("0.03"), "u3": D("0.03")},
    )
    check(
        "Single user: 1.00 ÷ 1 → [1.00]",
        split_equal(1.00, ["solo"]),
        {"solo": D("1.00")},
    )
    check(
        "Sum invariant: 10.00 ÷ 7 → must equal exactly 10.00",
        sum(split_equal(10.00, [f"u{i}" for i in range(7)]).values()) == D("10.00"),
        True,
    )
    expect_error("Empty user_ids",            split_equal, 100.0, [])
    expect_error("Duplicate user_ids",        split_equal, 100.0, ["a", "a"])
    expect_error("Zero total_amount",         split_equal, 0,     ["a"])
    expect_error("Negative total_amount",     split_equal, -50,   ["a", "b"])

    # ── Percentage Split ──────────────────────────────────────────────────
    print(f"\n{BOLD}━━━  2. Percentage Split  ━━━{RESET}")

    check(
        "70/30 on 200.00 → [140.00, 60.00]",
        split_percentage(200.00, {"alice": 70, "bob": 30}),
        {"alice": D("140.00"), "bob": D("60.00")},
    )
    check(
        "33.33/33.33/33.34 on 100.00 → exact match",
        split_percentage(100.00, {"a": D("33.33"), "b": D("33.33"), "c": D("33.34")}),
        {"a": D("33.33"), "b": D("33.33"), "c": D("33.34")},
    )
    check(
        "Repeating % (1/3 each) on 100.00 → sum == 100.00",
        sum(
            split_percentage(
                100.00,
                {"a": D("33.3333"), "b": D("33.3333"), "c": D("33.3334")},
            ).values()
        ) == D("100.00"),
        True,
    )
    expect_error("Percentages sum to 99",    split_percentage, 100.0, {"a": 50, "b": 49})
    expect_error("Percentages sum to 101",   split_percentage, 100.0, {"a": 60, "b": 41})
    expect_error("Negative percentage",      split_percentage, 100.0, {"a": 110, "b": -10})

    # ── Share-based Split ─────────────────────────────────────────────────
    print(f"\n{BOLD}━━━  3. Share-based Split  ━━━{RESET}")

    check(
        "2:1 shares on 90.00 → [60.00, 30.00]",
        split_shares(90.00, {"alice": 2, "bob": 1}),
        {"alice": D("60.00"), "bob": D("30.00")},
    )
    check(
        "1:1:1 shares on 10.00 → penny to first user [3.34, 3.33, 3.33]",
        split_shares(10.00, {"alice": 1, "bob": 1, "charlie": 1}),
        {"alice": D("3.34"), "bob": D("3.33"), "charlie": D("3.33")},
    )
    check(
        "Fractional shares (1.5:1) on 50.00 → [30.00, 20.00]",
        split_shares(50.00, {"alice": D("1.5"), "bob": 1}),
        {"alice": D("30.00"), "bob": D("20.00")},
    )
    check(
        "Sum invariant: 5 equal shares on 33.33 → must equal 33.33",
        sum(
            split_shares(33.33, {"a": 1, "b": 1, "c": 1, "d": 1, "e": 1}).values()
        ) == D("33.33"),
        True,
    )
    expect_error("Zero shares",     split_shares, 100.0, {"a": 0, "b": 1})
    expect_error("Negative shares", split_shares, 100.0, {"a": -1, "b": 2})

    # ── Exact Split ───────────────────────────────────────────────────────
    print(f"\n{BOLD}━━━  4. Exact Split  ━━━{RESET}")

    check(
        "60 + 40 = 100.00 → accepted as-is",
        split_exact(100.00, {"alice": 60.00, "bob": 40.00}),
        {"alice": D("60.00"), "bob": D("40.00")},
    )
    check(
        "Item-level amounts → exact values preserved",
        split_exact(45.75, {"alice": 20.00, "bob": 15.75, "charlie": 10.00}),
        {"alice": D("20.00"), "bob": D("15.75"), "charlie": D("10.00")},
    )
    check(
        "Single user pays everything",
        split_exact(99.99, {"solo": 99.99}),
        {"solo": D("99.99")},
    )
    expect_error("Amounts under-sum total",  split_exact, 100.0, {"a": 60.0, "b": 30.0})
    expect_error("Amounts over-sum total",   split_exact, 100.0, {"a": 60.0, "b": 50.0})
    expect_error("Negative exact amount",    split_exact, 100.0, {"a": 110.0, "b": -10.0})

    # ── Unified Dispatcher ────────────────────────────────────────────────
    print(f"\n{BOLD}━━━  5. Unified Dispatcher  ━━━{RESET}")

    check(
        "String 'equal' → EQUAL split",
        calculate_debt_distribution("equal", 10.00, user_ids=["x", "y"]),
        {"x": D("5.00"), "y": D("5.00")},
    )
    check(
        "Enum PERCENTAGE → PERCENTAGE split",
        calculate_debt_distribution(
            SplitMethod.PERCENTAGE, 50.00, user_percentages={"x": 60, "y": 40}
        ),
        {"x": D("30.00"), "y": D("20.00")},
    )
    check(
        "'shares' → SHARES split",
        calculate_debt_distribution("shares", 120.00, user_shares={"x": 3, "y": 1}),
        {"x": D("90.00"), "y": D("30.00")},
    )
    check(
        "'exact' → EXACT split",
        calculate_debt_distribution(
            "exact", 75.00, user_exact_amounts={"x": 50.00, "y": 25.00}
        ),
        {"x": D("50.00"), "y": D("25.00")},
    )
    expect_error("EQUAL without user_ids",   calculate_debt_distribution, "equal",  100.0)
    expect_error("Unknown method 'random'",  calculate_debt_distribution, "random", 100.0,
                 user_ids=["a"])

    # ── Summary ───────────────────────────────────────────────────────────
    total = results["passed"] + results["failed"]
    colour = GREEN if results["failed"] == 0 else RED
    print(
        f"\n{BOLD}{colour}"
        f"  Result: {results['passed']}/{total} tests passed"
        f"{RESET}\n"
    )
