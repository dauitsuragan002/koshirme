from aiogram import types
from config_bot import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

async def get_typing(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")

async def start_handler(message: types.Message):
    await get_typing(message)
    username = message.from_user.username or "қонақ"
    welcome_text = await message.answer(
        f"Сәлем, @{username}!\n\n*Сілтемеңізді жіберіңіз* немесе /download командасын басыңыз. Қай әлеуметтік желіден видео жүктеу керек екенін таңдаңыз.\n\nБот командалары '/' арқылы немесе 'МЕНЮ' батырмасы арқылы орындалады.",
        parse_mode='Markdown')
    await asyncio.sleep(20)
    await bot.delete_message(chat_id=welcome_text.chat.id, message_id=welcome_text.message_id)
    await asyncio.sleep(3600*24)
    await bot.delete_message(message.chat.id, message.message_id)

async def info_handler(message: types.Message):
    await get_typing(message)
    info_text = await message.answer(
        "Бұл боттың мақсаты — Қазақстандық қолданушыларға ыңғайлы, жарнамасыз видео жүктеу сервисін ұсыну.\n\n/more — Басқа боттарым туралы ақпарат.\n\nP.S. Командаларды '/' арқылы немесе 'МЕНЮ' батырмасы арқылы орындауға болады!\n\nБот авторы: @david667s")
    await asyncio.sleep(60)
    await bot.delete_message(chat_id=info_text.chat.id, message_id=info_text.message_id)
    await asyncio.sleep(2)
    await bot.delete_message(message.chat.id, message.message_id)

async def more_handler(message: types.Message):
    await get_typing(message)
    help_text = await message.answer(
        "\tМенің басқа да боттарым. Таныс болыңыз!\n\n 1.Ағылшын тілін ЖИ мен бірге үйрену - @englishkaz_bot\n\n2.Мәтінді қазақша тегін сөйлету - @qaztts_bot\n\nТолығырақ ақпарат алу үшін /info командасын қолданыңыз!")
    await asyncio.sleep(60)
    await bot.delete_message(chat_id=help_text.chat.id, message_id=help_text.message_id)
    await asyncio.sleep(2)
    await bot.delete_message(message.chat.id, message.message_id)

async def help_handler(message: types.Message):
    await get_typing(message)
    help_text = (
        "/info — Бот туралы ақпарат.\n"
        "/more — Басқа боттарым.\n"
        "/download — Қолжетімді желілерден видео жүктеу.\n\n"
        "Барлық командаларды '/' арқылы немесе 'МЕНЮ' батырмасы арқылы орындауға болады!"
    )
    await message.answer(help_text)

# /download
async def download_handler(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    service_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='YouTube', callback_data='youtube')],
            [InlineKeyboardButton(text="TikTok", url="https://t.me/tiktok667_bot?start=start")],
            [InlineKeyboardButton(text='Вконтакте', callback_data='вконтакте')]
        ]
    )
    await message.answer('Қай сервистен видео жүктегіңіз келеді?', reply_markup=service_keyboard)
