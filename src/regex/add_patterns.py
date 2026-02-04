import re

from src.regex.asset_name_patterns import base_name_re
from src.regex.price_patterns import re_int, re_float

parameter_price_re = re.compile(rf"-p\s+({re_float.pattern})")

add_asset_re = re.compile(
    rf"^/add\s+"
    rf"(stock|crypto|steam)\s+"
    rf"(?:({re_int.pattern})\s+)?"
    rf"({base_name_re.pattern})\s+"
    rf"({re_float.pattern})"
    rf"(?:\s+{parameter_price_re.pattern})?\s*$",
    re.IGNORECASE
)

