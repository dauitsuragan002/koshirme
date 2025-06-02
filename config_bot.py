import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()

token = os.getenv("TOKEN")
bot = Bot(token=token)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

BOT_USERNAME = os.getenv("BOT_USERNAME", "koshirme667_bot")

user_urls = {}