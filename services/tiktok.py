# Have a error 403 Forbidden
import re
import yt_dlp
from config_bot import bot, BOT_USERNAME
import clck
import asyncio
from aiogram import types
from aiogram.fsm.context import FSMContext

def is_tiktok_video(url):
    tiktok_regex = r"(https?://)?(www\.)?(tiktok|m\.tiktok)\.com/v/.*"
    tiktok_alternative_regex = r"(https?://)?(www\.)?(tiktok|m\.tiktok)\.com/@[\w.-]+/video/\d+.*"
    tiktok_share_regex = r"(https?://)?(www\.)?tiktok\.com/oembed.*"
    tiktok_short_url_regex = r"https://vm\.tiktok\.com/\w+/?"
    tiktok_webapp_regex = r"(https?://)?(www\.)?tiktok\.com/@[\w.-]+/video/\d+.*"
    return (
        re.match(tiktok_regex, url) is not None
        or re.match(tiktok_alternative_regex, url) is not None
        or re.match(tiktok_share_regex, url) is not None
        or re.match(tiktok_short_url_regex, url) is not None
        or re.match(tiktok_webapp_regex, url) is not None
    )

async def get_tiktok_url(response: types.Message, state: FSMContext):
    url = response.text
    file_name = None
    if is_tiktok_video(url):
        await bot.send_chat_action(response.chat.id, "upload_video")
        ydl_opts = {
            'quiet': True,
            'force_generic_extractor': True,
            'format': "url1080/url720/url480/url360/url240/bestvideo[ext=mp4]+bestaudio[ext=mp4]/best[ext=mp4]",
            'get-url': True,
            'errors': True
        }
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        info = ydl.extract_info(url, download=False)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            if 'url' in info_dict:
                direct_url = info_dict['url']
                thumbnail_url = info_dict.get('thumbnail')
                url_clck = clck.ru(direct_url)
                caption = f"*{info['title']}*\nҰзақтығы: {info['duration'] / 60:.2f} минут \n\n*@{BOT_USERNAME}*\n\n[Жүктеу]({url_clck})"
                await bot.send_photo(response.from_user.id, thumbnail_url, caption=caption, parse_mode="Markdown")
