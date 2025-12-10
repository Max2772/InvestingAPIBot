from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

PORTFOLIO_BUTTONS = {
    'All  🌐': 'all',
    'Stocks 💹': 'stocks',
    'Crypto ⚡': 'crypto',
    'Steam  🕹️': 'steam'
}

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=button) for button in PORTFOLIO_BUTTONS.keys()]
    ],
    resize_keyboard=True,
    input_field_placeholder='Choose a category for portfolio review..'
)
