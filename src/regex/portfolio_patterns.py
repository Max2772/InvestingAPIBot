import re

portfolio_re = re.compile(
    rf"^/portfolio\s+"
    rf"(all|stock|crypto|steam)\s*$"
)
