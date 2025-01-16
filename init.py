from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import os
from aiogram.enums import ParseMode
import google.generativeai as genai
from database import BotBD
import redis
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.http import models as modelsqd

load_dotenv()

genai.configure(api_key=f'{os.getenv("GEMINY_API_KEY")}')
model = genai.GenerativeModel('gemini-pro')

SERV = os.getenv("server") == 'production'

if SERV:
    API_TOKEN = os.getenv("API_TOKEN")
    TELEGRAM_API_URL = f'https://api.telegram.org/bot{API_TOKEN}/sendMessage'
else:
    API_TOKEN = os.getenv("API_TOKEN_Test")
    TELEGRAM_API_URL = f'https://api.telegram.org/bot{API_TOKEN}/sendMessage'

PASSWORD = os.getenv("PASSWORD")

URL = os.getenv("URL")
WebhookURL= os.getenv("WebhookURL")

AdminIDSerg = os.getenv("ADMIN_SERG")

AdminID = [AdminIDSerg,]
BroadcastURL = os.getenv("BroadcastURL")

modelEmbed = SentenceTransformer('all-MiniLM-L6-v2')

#client = QdrantClient(path="./qa_storage")
client = QdrantClient(host="192.168.1.10", port=6333)
collection_name = "orxid_collection"

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
DataBase = BotBD()
redis_client = redis.Redis(host='192.168.1.10', port=6379, db=0, decode_responses=True)

