"""
currency_service.py
===================
Multi-currency conversion service.

Currently a **placeholder** — returns a 1:1 conversion and logs a warning.
To activate real FX rates, plug in any of these providers:

  • Exchange Rates API  https://exchangeratesapi.io   (free tier available)
  • Open Exchange Rates https://openexchangerates.org
  • Fixer.io            https://fixer.io
  • frankfurter.app     https://www.frankfurter.app   (free, no key required)

Usage
-----
    from app.services.currency_service import convert_currency

    amount_in_usd = await convert_currency(
        amount=Decimal("100"),
        from_currency="EUR",
        to_currency="USD",
    )

Replace `_fetch_rate_from_api` below with your chosen provider's HTTP call.
"""

import logging
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

logger = logging.getLogger(__name__)

# ── In-memory cache (replace with Redis for production) ──────────────────────
_rate_cache: dict[str, Decimal] = {}


async def _fetch_rate_from_api(from_currency: str, to_currency: str) -> Optional[Decimal]:
    """
    PLACEHOLDER — wire this to a real Forex API.

    Example using frankfurter.app (no API key required):

        import httpx
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://api.frankfurter.app/latest",
                params={"from": from_currency, "to": to_currency},
            )
            r.raise_for_status()
            data = r.json()
            return Decimal(str(data["rates"][to_currency]))
    """
    # ── Stub: return None to trigger the 1:1 fallback ────────────────────────
    return None


async def convert_currency(
    amount: Decimal,
    from_currency: str,
    to_currency: str,
) -> Decimal:
    """
    Convert `amount` from `from_currency` to `to_currency`.

    - Uses a cached rate if available (cache TTL should be added for production).
    - Falls back to 1:1 rate with a warning when the API is not configured.
    - Always returns a Decimal rounded to 2 decimal places.

    Parameters
    ----------
    amount : Decimal
        The amount to convert.
    from_currency : str
        ISO 4217 source currency code, e.g. "EUR".
    to_currency : str
        ISO 4217 target currency code, e.g. "USD".

    Returns
    -------
    Decimal
        Converted amount rounded to 2 d.p.
    """
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    cache_key = f"{from_currency}_{to_currency}"

    if cache_key not in _rate_cache:
        rate = await _fetch_rate_from_api(from_currency, to_currency)
        if rate is None:
            logger.warning(
                "FX rate not available for %s→%s — using 1:1 fallback. "
                "Configure a Forex API in currency_service.py.",
                from_currency,
                to_currency,
            )
            rate = Decimal("1")
        _rate_cache[cache_key] = rate

    converted = amount * _rate_cache[cache_key]
    return converted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def invalidate_rate_cache() -> None:
    """Clear the in-memory rate cache (call periodically, e.g., in a scheduler)."""
    _rate_cache.clear()
    logger.info("FX rate cache cleared")
