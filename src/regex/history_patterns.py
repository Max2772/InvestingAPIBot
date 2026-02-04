import re

history_re = re.compile(
    rf"^/history\s+"
    rf"(all|stock|crypto|steam)$"
)
