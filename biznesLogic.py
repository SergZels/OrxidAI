from aiogram import Router, F, types
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from aiogram.enums import ChatAction
import logging
from qdrant import find_answer
from init import TELEGRAM_API_URL, model,DataBase,bot,AdminIDSerg
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

def prepare_prompt(user_message: str) -> str:
    return f"""Твоя роль цифровий менеджер ательє Орхідея. На основі наступної інформації про компанію, дай відповідь на запитання клієнта.
    Відповідай виключно українською мовою. Якщо інформації недостатньо, попроси уточнити запитання. Якщо інформація відсутня то скажи "Нажаль не маю інформації по вашому запитанню. Зателефонуйтте в ательє 067777777".
    Якщо клієнт вітається то привітайся з ним. (Доброго дня!). Якщо клієнт дякує то відповідай (Будь ласка! Заходіть будемо раді вас бачити!).
    
    Загальна інформація про компанію:
    Ательє Орхідея займається пошиттям і ремонтом одягу та прокатом костюмів. Працює на ринку з 2002 року.
    Адреса: вул. 22 січня, 17а (біля стадіону) телефон 067777777 email: zelse@ukr.net
    Графік роботи: пн-пт 9:00-18:00, сб 9:00-15:00, нд та дні релігійних свят вихідний
    
    Детальніша інформація про компанію із векторної бази знань:
    {find_answer(user_message, top_k=2)}
    

    Запитання клієнта: {user_message}
    """

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
    await message.answer("Вітаю! Я бот вашої фірми. Задайте будь-яке запитання, і я спробую вам допомогти!")

    if await DataBase.is_subscriber_exists(message.from_user.id) == False:
        await DataBase.add_subscriber(message.from_user.id, message.from_user.username)
        #await bot.send_message(AdminIDSerg, f"Новенький підписався! Нік - {message.from_user.username}")



@router.message()
async def handle_question(message: Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    prompt = prepare_prompt(message.text)
    bot_response = model.generate_content(prompt)
    await message.answer(bot_response.text)


@router.message(F.text.lower() == "/help")
async def answer_yes(message: Message):
    await message.answer("Для отримання допомоги напишіть на @SZelinsky\nРозробка телеграм ботів та іншого софту - <a href='https://zelse.asuscomm.com/PortfolioReact/'>Сергій</a> ", parse_mode="HTML", disable_web_page_preview=True )
    logger.info(f"Корстувач {message.from_user.username} відкрив help")



@router.callback_query(F.data == "file12")
async def file12(callback: types.CallbackQuery):
    file = FSInputFile("Logfile.txt")
    await callback.message.answer_document(document=file)






