"""
currency_service.py
====================
Multi-currency conversion placeholder.

This module provides a `convert_currency` function that will eventually call an
external Forex API (e.g., exchangeratesapi.io, openexchangerates.org).

Current behaviour:
  • Same-currency conversions return the original amount (no-op).
  • Cross-currency conversions raise NotImplementedError until a real provider
    is wired in.

Integration guide:
  1. Add your API key to .env  →  FOREX_API_KEY=...
  2. Implement `_fetch_rate(from_cur, to_cur)` below.
  3. Add optional caching (Redis / in-memory TTL dict) to avoid per-request
     HTTP round-trips.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

# ---------------------------------------------------------------------------
# Stub exchange-rate store (replace with live API call)
# ---------------------------------------------------------------------------

# TODO: Replace with httpx call to a Forex REST API.
#       Example providers:
#         • https://exchangeratesapi.io/
#         • https://openexchangerates.org/
#         • https://www.frankfurter.app/  (free, no key)


async def _fetch_rate(from_currency: str, to_currency: str) -> Decimal:
    """
    Fetch the live exchange rate from `from_currency` to `to_currency`.

    Returns
    -------
    Decimal
        The multiplicative conversion factor.

    Raises
    ------
    NotImplementedError
        Until a real API is integrated.
    """
    raise NotImplementedError(
        f"Live FX rate lookup ({from_currency} → {to_currency}) is not yet "
        f"implemented. Wire up a Forex API provider in currency_service.py."
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def convert_currency(
    amount: Decimal,
    from_currency: str,
    to_currency: str,
    *,
    rate_override: Optional[Decimal] = None,
) -> Decimal:
    """
    Convert *amount* from one ISO-4217 currency to another.

    Parameters
    ----------
    amount : Decimal
        The monetary value to convert.
    from_currency : str
        3-letter ISO currency code of the source (e.g. "USD").
    to_currency : str
        3-letter ISO currency code of the target (e.g. "EUR").
    rate_override : Decimal, optional
        If supplied, skip the API call and use this rate directly.
        Useful for unit tests and batch processing with a known rate.

    Returns
    -------
    Decimal
        Converted amount rounded to 2 decimal places.
    """
    from_currency = from_currency.upper().strip()
    to_currency = to_currency.upper().strip()

    if from_currency == to_currency:
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    rate = rate_override if rate_override is not None else await _fetch_rate(from_currency, to_currency)
    converted = amount * rate
    return converted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


async def get_supported_currencies() -> list[str]:
    """
    Return the list of currency codes supported by the configured provider.

    Placeholder — returns a static list of common currencies.
    """
    return [
        "USD", "EUR", "GBP", "INR", "JPY", "CAD", "AUD",
        "CHF", "CNY", "SGD", "HKD", "SEK", "NOK", "DKK",
        "NZD", "ZAR", "BRL", "KRW", "MXN", "THB",
    ]
