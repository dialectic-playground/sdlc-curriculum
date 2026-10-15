"""Shared model of the car-sales day for dp-cars1 and dp-cars2 (Projects 26 and 28).

Projects 26 and 28 specify the same dialog, the same rejected-sale rules, and the same
``DAILY REPORT``; SRS-28 requires dp-cars2's default behavior to equal dp-cars1's byte for
byte (apart from the tool name in diagnostics). Keeping one model here makes that requirement
hold in the reference by construction. The report is rendered by :func:`render_report`, which
receives the two totals sequences and nothing else (SRS-28 NFR-05).
"""

from __future__ import annotations

from collections.abc import Sequence

from .common import InputStream, Token, encode_arg, err, fix, parse_int_token, prompt

BRANDS = 12
MAX_STOCK = 999_999
STOCK_PROMPT = "Cars in stock for brand: {brand}\n"
BRAND_PROMPT = "Which brand was sold? "
QUANTITY_PROMPT = "How many cars in sale? "
REPORT_TITLE = "DAILY REPORT"
REPORT_HEADING = "Brand    Start    Sales      End      Sales %"


def warn(tool: str, source: str, token: Token, message: bytes) -> None:
    """A rejected-sale diagnostic: CONV-34 format, but processing continues."""
    err.write(
        encode_arg(f"{tool}: {source}:{token.line}: ")
        + message
        + b" '"
        + token.text
        + b"'\n"
    )
    err.flush()


def read_day(
    reader: InputStream, source: str, prompting: bool, tool: str
) -> tuple[list[int], list[int], bool]:
    """Opening stock, then sales until a negative brand or the end of input.

    Returns (stock, sales, rejected), where ``rejected`` tells whether any sale was rejected.
    Raises DataError for invalid tokens and for an input that ends too early.
    """
    stock = []
    for brand in range(BRANDS):
        prompt(prompting, STOCK_PROMPT.format(brand=brand))
        stock.append(parse_int_token(reader.require(source), source, 0, MAX_STOCK))
    sales = [0] * BRANDS
    rejected = False
    while True:
        prompt(prompting, BRAND_PROMPT)
        brand_token = reader.token()
        if brand_token is None:
            break
        brand = parse_int_token(brand_token, source)
        if brand < 0:
            break
        prompt(prompting, QUANTITY_PROMPT)
        quantity_token = reader.require(source)
        quantity = parse_int_token(quantity_token, source)
        if brand >= BRANDS:
            warn(tool, source, brand_token, b"no such brand")
        elif quantity < 0:
            warn(tool, source, quantity_token, b"negative quantity")
        elif quantity > stock[brand] - sales[brand]:
            warn(
                tool,
                source,
                quantity_token,
                f"not enough cars in stock for brand {brand}".encode(),
            )
        else:
            sales[brand] += quantity
            continue
        rejected = True
    return stock, sales, rejected


def percentage(start: int, sold: int) -> str:
    """FIX(100 x sold / start, 6) followed by %, or n/a when the opening stock is zero."""
    if start == 0:
        return "n/a"
    return (
        fix(100 * sold / start, 6) + "%"
    )  # exact operands, one correctly rounded division


def render_report(stock: Sequence[int], sales: Sequence[int]) -> str:
    """The DAILY REPORT for the given opening stock and sales totals (read-only inputs)."""
    lines = [REPORT_TITLE, REPORT_HEADING]
    for brand, (start, sold) in enumerate(zip(stock, sales)):
        lines.append(
            f"{brand:5d}{start:9d}{sold:9d}{start - sold:9d}"
            f"{percentage(start, sold):>13}"
        )
    return "\n".join(lines) + "\n"
