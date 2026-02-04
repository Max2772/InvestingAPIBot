from typing import Optional

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.types.dto.help_cb import HelpCb
from src.types.dto.portfolio_cb import PortfolioCb
from src.types.labels import PORTFOLIO_SECTION_TITLES
from src.types.response_enums import AssetType
from src.utils.tg_utils import edit_content

_KB_MAIN_MENU: Optional[InlineKeyboardMarkup] = None

CAPTION_MAIN_MENU = (
        f"<b>Main menu</b>\n"
        f"Choose an action 👇"
)

def create_main_menu_kb() -> InlineKeyboardMarkup:
    global _KB_MAIN_MENU
    if _KB_MAIN_MENU is None:
        keyboard = [
            [InlineKeyboardButton(text="❓ Help", callback_data=HelpCb().pack())],
            [InlineKeyboardButton(text="📜 All Portfolio", callback_data=PortfolioCb(asset_type=AssetType.ALL).pack())],
        ]

        for asset_type, title in PORTFOLIO_SECTION_TITLES.items():
            keyboard.append([
                InlineKeyboardButton(
                    text=f"{title} Portfolio",
                    callback_data=PortfolioCb(asset_type=asset_type).pack(),
                )
            ])

        _KB_MAIN_MENU = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return _KB_MAIN_MENU


async def open_main_menu(message: types.Message, edit: bool = False):
    if edit:
        await edit_content(
            message,
            CAPTION_MAIN_MENU,
            kb=create_main_menu_kb()
        )
    else:
        await message.answer(
            CAPTION_MAIN_MENU,
            reply_markup=create_main_menu_kb()
        )