import re

from src.regex.asset_name_patterns import base_name_re
from src.regex.price_patterns import re_int

check_asset_re = re.compile(
    rf"^/check\s+"
    rf"(stock|crypto|steam)\s+"
    rf"(?:({re_int.pattern})\s+)?"
    rf"({base_name_re.pattern})\s*$"
)
