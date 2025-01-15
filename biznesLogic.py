from aiogram import Router, F, types
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from aiogram.enums import ChatAction
import logging
from qdrant import find_answer
from init import TELEGRAM_API_URL, model,DataBase,bot,AdminIDSerg, redis_client
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

def prepare_prompt(user_message: str, vectorData, conversational) -> str:
    return f"""Твоя роль цифровий менеджер ательє Орхідея. На основі наступної інформації про компанію, дай відповідь на запитання клієнта.
    Відповідай виключно українською мовою. Якщо інформації недостатньо, попроси уточнити запитання. Якщо інформація відсутня то скажи "Нажаль не маю інформації по вашому запитанню. Зателефонуйтте в ательє 097 65 38 200". Номер власниці ательє Орхідея 0976538805 Тетяна.
    Якщо клієнт вітається то привітайся з ним. (Доброго дня!). Якщо клієнт дякує то відповідай (Будь ласка! Заходіть будемо раді вас бачити!).
    
    Загальна інформація про компанію:
    Ательє Орхідея займається пошиттям і ремонтом одягу та прокатом костюмів. Також у нас діє магазин швейної фурнітури та багетна майстерня. Девіз - досвід професійність та сервіс. Працює на ринку з 2002 року.
    Адреса: вул. 22 січня, 17а (біля стадіону) телефон 097 65 38 200 email: zelse@ukr.net сайт🌍: orxid.in.ua
    Графік роботи 📆: пн-пт 9:00-18:00, сб 9:00-15:00, нд та дні релігійних свят вихідний. Працюємо без обіду.
    
    Детальніша інформація про компанію із векторної бази знань:
    { vectorData}
    
    Якщо у даних із векторної бази є зсилка на youtube то включи її у відповідь.,
    Якщо клієнт буде уточнювати чи є товар на складі, то відповідайт, що не володієш інформацією про наявність і давай номер телефону на фірму.
    Також по можливості старайся додати смайлики та емодзі у відповіді.
    
    Запитання клієнта: {user_message}
    
    Контекст, попередня переписка: {conversational}
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



def add_message(user_id, sender, message):
    # Redis зберігає історію для кожного користувача як список
    key = f"conversation:{user_id}"  # Ключ для користувача

    # Створення словника повідомлення
    message_data = {"sender": sender, "message": message}

    # Додаємо повідомлення в список Redis
    redis_client.rpush(key, str(message_data))  # додаємо в кінець списку

    # Обмежуємо довжину списку до 10 останніх повідомлень
    redis_client.ltrim(key, -5, -1)  # зберігаємо лише 5 останніх

def get_last_messages(user_id):
    key = f"conversation:{user_id}"

    # Отримуємо останні 10 повідомлень з Redis
    messages = redis_client.lrange(key, 0, -1)

    # Перетворюємо збережені повідомлення з рядків у словники
    messages = [eval(msg) for msg in messages]
    return messages


@router.message(CommandStart())
async def send_welcome(message: Message):
    await message.answer("Вітаю! Я розумний бот ательє Орхідея. Задайте будь-яке запитання, і я спробую вам допомогти!")

    if await DataBase.is_subscriber_exists(message.from_user.id) == False:
        await DataBase.add_subscriber(message.from_user.id, message.from_user.username)
        #await bot.send_message(AdminIDSerg, f"Новенький підписався! Нік - {message.from_user.username}")


@router.message()
async def handle_question(message: Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    cache_key = f"response:{message.text.strip().lower()}"

    cached_response = redis_client.get(cache_key)
    if cached_response:
        await message.answer(cached_response)
        return

    add_message(message.from_user.id, "user", message.text)
    # Якщо немає в кеші, генеруємо відповідь
    vectorData = find_answer(message.text, top_k=2)
    conversational = get_last_messages(message.from_user.id)
    prompt = prepare_prompt(message.text, vectorData, conversational)
    print(prompt)
    bot_response = model.generate_content(prompt)
    add_message(message.from_user.id, "bot", f"відповідь бота: {bot_response.text} та дані із векторної бази {vectorData}")
    # Зберігаємо відповідь у Redis (наприклад, на 1 годину)
    redis_client.setex(cache_key, 3600, bot_response.text)
    logger.info(f"Користувач {message.from_user.username} запитав: {message.text}\nБот відповів: ")
    await message.answer(bot_response.text)


@router.message(F.text.lower() == "/help")
async def answer_yes(message: Message):
    await message.answer("Для отримання допомоги напишіть на @SZelinsky\nРозробка телеграм ботів та іншого софту - <a href='https://zelse.asuscomm.com/PortfolioReact/'>Сергій</a> ", parse_mode="HTML", disable_web_page_preview=True )
    logger.info(f"Корстувач {message.from_user.username} відкрив help")



@router.callback_query(F.data == "file12")
async def file12(callback: types.CallbackQuery):
    file = FSInputFile("Logfile.txt")
    await callback.message.answer_document(document=file)






