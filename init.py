from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import os
from aiogram.enums import ParseMode
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=f'{os.getenv("GEMINY_API_KEY")}')
model = genai.GenerativeModel('gemini-pro')

SERV = os.getenv("server") == 'production'

if SERV:
    API_TOKEN = os.getenv("API_TOKEN")
    TELEGRAM_API_URL = f'https://api.telegram.org/bot{API_TOKEN}/sendMessage'
else:
    API_TOKEN = os.getenv("API_TOKEN")
    TELEGRAM_API_URL = f'https://api.telegram.org/bot{API_TOKEN}/sendMessage'

PASSWORD = os.getenv("PASSWORD")

URL = os.getenv("URL")
WebhookURL= os.getenv("WebhookURL")

AdminIDSerg = os.getenv("ADMIN_SERG")
AdminIDJulia = os.getenv("ADMIN_Julia")
AdminID = [AdminIDSerg, AdminIDJulia]
BroadcastURL = os.getenv("BroadcastURL")
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

