import re
from aiogram import types
from config_bot import bot, BOT_USERNAME
from aiogram.fsm.context import FSMContext
import yt_dlp
from aiogram.types import FSInputFile
import hashlib
import os

# Instagram сілтемесін анықтау
INSTAGRAM_REGEX = r"(https?://)?(www\.)?instagram\.com/(p|reel|tv)/[\w-]+"

def is_instagram_video(url):
    return re.match(INSTAGRAM_REGEX, url) is not None

async def get_instagram_url(response: types.Message, state: FSMContext):
    url = response.text
    await bot.send_chat_action(response.chat.id, "upload_video")
    loading_message = await bot.send_message(response.chat.id, "Видео жүктеліп жатыр, күте тұрыңыз...")
    file_name = None
    try:
        hash_name = hashlib.md5(url.encode()).hexdigest()
        file_name = f"{hash_name}.mp4"
        ydl_opts = {
            'format': 'mp4',
            'outtmpl': file_name,
            'noplaylist': True,
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
        file_size = os.path.getsize(file_name)
        if file_size > 50 * 1024 * 1024:
            direct_url = info_dict.get('url')
            if direct_url:
                await bot.send_message(response.chat.id, f'Видео көлемі 50 МБ-тан асады, Telegram арқылы жіберу мүмкін емес.\nТікелей жүктеу сілтемесі: {direct_url}')
            else:
                await bot.send_message(response.chat.id, 'Видео көлемі 50 МБ-тан асады, бірақ тікелей сілтемені алу мүмкін болмады.')
        else:
            video_file = FSInputFile(file_name)
            await bot.send_video(response.chat.id, video=video_file, caption=f'Instagram видеосы дайын!\n\n@{BOT_USERNAME}')
    except Exception as e:
        print(f"Error: {e}")
        await bot.send_message(response.chat.id, 'Instagram видеосын жүктеу кезінде қате шықты.')
    finally:
        if file_name:
            os.remove(file_name)
        await bot.delete_message(response.chat.id, loading_message.message_id)
    await state.clear()
