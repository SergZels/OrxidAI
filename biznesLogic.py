from aiogram import Router, F, types
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.deep_linking import decode_payload
from aiogram.utils.deep_linking import create_start_link
import re
import logging
from qdrant import find_answer
import os
from datetime import datetime
from init import bot, AdminID, AdminIDJulia, AdminIDSerg, TELEGRAM_API_URL, BroadcastURL, model
import aiohttp
import asyncio

router = Router()


class AsyncFileHandler(logging.FileHandler):  # для асинхронного логування
    def emit(self, record):
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, super().emit, record)


logger = logging.getLogger('async_logger')
logger.setLevel(logging.INFO)
handler = AsyncFileHandler('Logfile.txt')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


async def send_telegram_message(chat_id, text):
    payload = {
        'chat_id': chat_id,
        'text': text
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(TELEGRAM_API_URL, json=payload) as response:
                response.raise_for_status()  # Якщо статус відповіді не 200, підніме виключення
                logger.info(f"Надіслано повідомлення користувачу {chat_id}")
                return await response.json()  # Чекаємо на парсинг JSON

        except aiohttp.ClientError as e:
            logger.info(f"Помилка при надсиланні телеграм повідомлення до {chat_id}: {e}")
            print(f"Помилка при надсиланні телеграм повідомлення до {chat_id}: {e}")
            return None


@router.message(CommandStart())
async def send_welcome(message: Message):
    await message.reply("Вітаю! Я бот вашої фірми. Задайте будь-яке запитання, і я спробую вам допомогти!")

def prepare_prompt(user_message: str) -> str:
    return f"""На основі наступної інформації про компанію, дай відповідь на запитання клієнта.
    Відповідай лаконічно та по суті і виключно українською мовою. Якщо інформації недостатньо, попроси уточнити запитання.

    Інформація про компанію:
    {find_answer(user_message, top_k=1)}

    Запитання клієнта: {user_message}
    """

@router.message()
async def handle_question(message: Message):
    prompt = prepare_prompt(message.text)
    bot_response = model.generate_content(prompt)
    await message.reply(bot_response.text)



@router.message(F.text.lower() == "/help")
async def answer_yes(message: Message):
    await message.answer("Для отримання допомоги напишіть на @SZelinsky\nРозробка телеграм ботів та іншого софту - <a href='https://zelse.asuscomm.com/PortfolioReact/'>Сергій</a> ", parse_mode="HTML", disable_web_page_preview=True )
    logger.info(f"Корстувач {message.from_user.username} відкрив help")



@router.callback_query(F.data == "file12")
async def file12(callback: types.CallbackQuery):
    file = FSInputFile("Logfile.txt")
    await callback.message.answer_document(document=file)






