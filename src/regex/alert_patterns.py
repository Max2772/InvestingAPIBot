import re

from src.regex.price_patterns import re_int, re_float
from src.regex.asset_name_patterns import base_name_re

set_alert_re = re.compile(
    rf"^/set_alert\s+"
    rf"(stock|crypto|steam)\s+"
    rf"(?:({re_int.pattern})\s+)?"
    rf"({base_name_re.pattern})\s+"
    rf"(>|>=|<|<=)\s+"
    rf"({re_float.pattern})\s*$",
    re.IGNORECASE
)

delete_alert_re = re.compile(
    rf"^/delete_alert\s+({re_int.pattern})$",
    re.IGNORECASE
)
