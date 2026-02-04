import asyncio
from decimal import Decimal
from typing import Optional

from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, InlineKeyboardMarkup, Update, User


async def validate_amount_and_price(
    message: Message,
    amount: Decimal,
    price: Decimal | None
) -> bool:
    if amount <= 0:
        await message.answer("Amount must be positive!")
        return False

    if price and price <= 0:
        await message.answer("Price must be positive!")
        return False
    return True


async def cq_answer(
        cq: types.CallbackQuery,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None
):
    await cq.answer(text, show_alert=show_alert)


async def edit_content(
        message: types.Message,
        new_text: str,
        *,
        kb: Optional[InlineKeyboardMarkup] = None,
        no_img: bool = False
):
    try:
        if (message.caption and no_img) or (not message.caption and not message.text):
            await asyncio.gather(
                safe_delete(message),
                message.bot.send_message(
                    chat_id=message.chat.id,
                    text=new_text,
                    reply_markup=kb,
                )
            )
            return
        if message.caption:
            await message.edit_caption(
                caption=new_text,
                reply_markup=kb or message.reply_markup
            )
            return
        else:
            await message.edit_text(
                text=new_text,
                reply_markup=kb or message.reply_markup
            )

    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            return
        raise

async def safe_delete(message: Message):
    try:
        await message.delete()
    except:
        pass

def extract_user(update: Update) -> Optional[User]:
    if update.message:
        return update.message.from_user

    if update.edited_message:
        return update.edited_message.from_user

    if update.callback_query:
        return update.callback_query.from_user

    if update.inline_query:
        return update.inline_query.from_user

    if update.chosen_inline_result:
        return update.chosen_inline_result.from_user

    if update.shipping_query:
        return update.shipping_query.from_user

    if update.pre_checkout_query:
        return update.pre_checkout_query.from_user

    if update.poll_answer:
        return update.poll_answer.user

    if update.my_chat_member:
        return update.my_chat_member.from_user

    if update.chat_member:
        return update.chat_member.from_user

    if update.chat_join_request:
        return update.chat_join_request.from_user

    return None