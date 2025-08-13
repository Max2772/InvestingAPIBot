def profit_emoji(value):
    return '📈' if value > 0 else '📉' if value < 0 else ''

def profit_sign(value):
    return '+' if value > 0 else '-' if value < 0 else ''