from decimal import Decimal

from src.logger import get_logger


logger = get_logger()

float_price_pattern = r"\d+(?:\.\d+)?"
science_price_pattern = r"\d+(?:\.\d+)?|\d+(?:\.\d+)?[eE][+-]\d+"


def profit_emoji(value: Decimal) -> str:
    return ' 📈' if value > 0 else ' 📉' if value < 0 else ''

def profit_sign(value: Decimal) -> str:
    return '+' if value > 0 else ''