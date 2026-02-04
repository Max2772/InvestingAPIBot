import re

stock_name_re = re.compile(r"[A-Za-z0-9.]+")
crypto_name_re = re.compile(r"[A-Za-z0-9-. ]+")
base_name_re = steam_name_re = re.compile(r".+?")