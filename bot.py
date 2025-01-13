from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import google.generativeai as genai
from qdrant import find_answer
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=f'{os.getenv("GEMINY_API_KEY")}')
model = genai.GenerativeModel('gemini-pro')
dp = Dispatcher()

@dp.message(CommandStart())
async def send_welcome(message: Message):
    await message.reply("Вітаю! Я бот вашої фірми. Задайте будь-яке запитання, і я спробую вам допомогти!")

def prepare_prompt(user_message: str) -> str:
    return f"""На основі наступної інформації про компанію, дай відповідь на запитання клієнта.
    Відповідай лаконічно та по суті і виключно українською мовою. Якщо інформації недостатньо, попроси уточнити запитання.

    Інформація про компанію:
    {find_answer(user_message, top_k=1)}

    Запитання клієнта: {user_message}
    """

@dp.message()
async def handle_question(message: Message):
    prompt = prepare_prompt(message.text)
    bot_response = model.generate_content(prompt)
    await message.reply(bot_response.text)

async def main() -> None:
    bot = Bot(token=f'{os.getenv("BOT_TOKEN")}', default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Бот запущено!")
    import asyncio
    asyncio.run(main())
