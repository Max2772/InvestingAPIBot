from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from src.configuration.bot_init import dp


@dp.message(Command('help'))
async def help_handler(message: Message):
    help_text = (
        "<b>📚 Bot Commands</b>\n\n"
        "<b>ℹ️ Help</b>\n"
        "  /help - Show this help message with all commands\n\n"
        "<b>🔑 Registration</b>\n"
        "  /start, /register - Register to start tracking your portfolio\n\n"
        "<b>💹 Check Prices</b>\n"
        "  /check_stock <code>ticker</code> - Get current stock price (e.g., /check_stock AMD)\n"
        "  /check_crypto <code>coin</code> - Get current crypto price (e.g., /check_crypto ETH)\n"
        "  /check_steam <code>app_id</code> <code>market_name</code> - Get Steam item price (e.g., /check_steam 730 Danger Zone Case)\n\n"
        "<b>📊 Portfolio Management</b>\n"
        "  /add_stock <code>ticker</code> <code>quantity</code> - Add stock to portfolio (e.g., /add_stock AMD 2)\n"
        "  /add_crypto <code>coin</code> <code>quantity</code> - Add crypto to portfolio (e.g., /add_crypto ETH 0.5)\n"
        "  /add_steam <code>app_id</code> <code>market_name</code> <code>quantity</code> - Add Steam item to portfolio (e.g., /add_steam 730 Danger Zone Case 10)\n"
        "  /remove_stock <code>ticker</code> <code>quantity</code> - Remove stock from portfolio\n"
        "  /remove_crypto <code>coin</code> <code>quantity</code> - Remove crypto from portfolio\n"
        "  /remove_steam <code>app_id</code> <code>market_name</code> <code>quantity</code> - Remove Steam item from portfolio\n"
        "  /portfolio <code>all|stocks|crypto|steam|total</code> - View portfolio (e.g., /portfolio stocks)\n\n"
        "<b>🔔 Price Alerts</b>\n"
        "<b>/set_alert</b> <code>asset_type</code> [<code>app_id</code>] <code>asset_name</code> <code>condition</code> <code>price</code> - Set a price alert\n"
        "  • <b>asset_type</b>: <code>stock</code>, <code>crypto</code>, or <code>steam</code>\n"
        "  • <b>app_id</b>: Required for Steam items (e.g., <code>730</code> for CS:GO)\n"
        "  • <b>condition</b>: <code>&gt;</code>, <code>&gt;=</code>, <code>&lt;</code>, or <code>&lt;=</code>\n"

        "  • Example: <code>/set_alert stock AMD > 200</code>\n"
        "  • Example: <code>/set_alert steam 730 Glove Case > 5</code>\n\n"
        "<b>/alerts</b> - Show all active alerts\n"
        "<b>/delete_alert</b> <code>id</code> - Remove an alert by ID\n"
        "  • Example: <code>/delete_alert 1</code>\n\n"
        "<b>📜 History</b>\n"
        "  /history <code>all|stocks|crypto|steam</code> - View purchase history (e.g., /history stocks)\n\n"
        "◇───────────────────────────────────────────◇\n"
        "<b>💡 Tip:</b> Use exact asset names and valid quantities/prices."
    )
    await message.answer(help_text, parse_mode=ParseMode.HTML)