from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from src.configuration.bot_init import dp


@dp.message(Command('help'))
async def help_handler(message: Message):
    help_text = (
    "<b>📚 Bot Commands</b>\n\n"

    "<b>ℹ️ Help</b>\n"
    "  • /help\n"
    "    ➝ Show this help message with all commands\n\n"

    "<b>🔑 Registration</b>\n"
    "  • /start, /register\n"
    "    ➝ Register to start tracking your portfolio\n\n"

    "<b>💹 Check Prices</b>\n"
    "  • /check_stock <code>ticker</code>\n"
    "    ➝ Get current stock price\n"
    "    Example: <code>/check_stock AMD</code>\n\n"
    "  • /check_crypto <code>coin</code>\n"
    "    ➝ Get current crypto price\n"
    "    Example: <code>/check_crypto ETH</code>\n\n"
    "  • /check_steam <code>app_id</code> <code>market_name</code>\n"
    "    ➝ Get Steam item price\n"
    "    Example: <code>/check_steam 730 Danger Zone Case</code>\n\n"

    "<b>📊 Portfolio Management</b>\n"
    "  You can use the optional <code>-p &lt;price&gt;</code> parameter to set your own purchase price "
    "(e.g., <code>-p 170</code> or <code>-p 170.50</code>).\n\n"
    "  • /add_stock <code>ticker</code> <code>quantity</code> [-p <code>price</code>]\n"
    "    ➝ Add stock to portfolio\n"
    "    Example: <code>/add_stock AMD 2</code>, <code>/add_stock AMD 20 -p 170.50</code>\n\n"
    "  • /add_crypto <code>coin</code> <code>quantity</code> [-p <code>price</code>]\n"
    "    ➝ Add cryptocurrency to portfolio\n"
    "    Example: <code>/add_crypto ETH 0.5</code>, <code>/add_crypto ETH 0.5 -p 2500.75</code>\n\n"
    "  • /add_steam <code>app_id</code> <code>market_name</code> <code>quantity</code> [-p <code>price</code>]\n"
    "    ➝ Add Steam item to portfolio\n"
    "    Example: <code>/add_steam 730 \"Danger Zone Case\" 10</code>, <code>/add_steam 730 \"Danger Zone Case\" 10 -p 2.99</code>\n\n"
    "  • /remove_stock <code>ticker</code> <code>quantity</code>\n"
    "    ➝ Remove stock from portfolio\n\n"
    "  • /remove_crypto <code>coin</code> <code>quantity</code>\n"
    "    ➝ Remove cryptocurrency from portfolio\n\n"
    "  • /remove_steam <code>app_id</code> <code>market_name</code> <code>quantity</code>\n"
    "    ➝ Remove Steam item from portfolio\n\n"
    "  • /portfolio <code>all|stocks|crypto|steam|total</code>\n"
    "    ➝ View your portfolio\n"
    "    Example: <code>/portfolio stocks</code>\n\n"

    "<b>🔔 Price Alerts</b>\n"
    "  • /set_alert <code>asset_type</code> [<code>app_id</code>] <code>asset_name</code> <code>condition</code> <code>price</code>\n"
    "    ➝ Set a price alert\n"
    "    ▸ <b>asset_type</b>: <code>stock</code>, <code>crypto</code>, or <code>steam</code>\n"
    "    ▸ <b>app_id</b>: Required for Steam items (e.g., <code>730</code> for CS:GO)\n"
    "    ▸ <b>condition</b>: <code>&gt;</code>, <code>&gt;=</code>, <code>&lt;</code>, or <code>&lt;=</code>\n"
    "    Example: <code>/set_alert stock AMD > 200</code>\n"
    "    Example: <code>/set_alert steam 730 Glove Case > 5</code>\n\n"
    "  • /alerts\n"
    "    ➝ Show all active alerts\n\n"
    "  • /delete_alert <code>id</code>\n"
    "    ➝ Remove an alert by ID\n"
    "    Example: <code>/delete_alert 1</code>\n\n"

    "<b>📜 History</b>\n"
    "  • /history <code>all|stocks|crypto|steam</code>\n"
    "    ➝ View purchase history\n"
    "    Example: <code>/history stocks</code>\n\n"

    "◇───────────────────────────────────────────◇\n"
    "<b>💡 Tip:</b> Use exact asset names and valid quantities/prices."
    )
    await message.answer(help_text, parse_mode=ParseMode.HTML)