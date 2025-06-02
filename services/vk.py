import re
import yt_dlp
from config_bot import bot, BOT_USERNAME
import clck
import asyncio
from aiogram import types
from aiogram.fsm.context import FSMContext
import subprocess

def is_vk_video(url):
    vk_video_regex = r"(https?://)?(www\.)?(vk\.com|vkvideo\.ru)/video-?\d+_\d+"
    vk_alternative_regex = r"(https?://)?(www\.)?(vk\.com|vkvideo\.ru)/video/\@d+_\d+"
    return (
        re.match(vk_video_regex, url) is not None
        or re.match(vk_alternative_regex, url) is not None
    )

def is_vk_wall(url):
    vk_wall_regex = r"(https?://)?(www\.)?(vk\.com|vkvideo\.ru)/wall-?\d+_\d+"
    return re.match(vk_wall_regex, url) is not None

def is_vk_playlist(url):
    vk_playlist_regex = r"https?://(www\.)?(vk\.com|vkvideo\.ru)/(video/playlist|playlist)/-\d+_\d+"
    return re.match(vk_playlist_regex, url) is not None

async def get_direct_video_url(response: types.Message, state: FSMContext):
    url = response.text
    info_dict = None
    if is_vk_video(url):
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
                caption = f"*{info['title']}*\nҰзақтығы: {info['duration'] / 60:.2f} минут \n\n*@koshirme667_bot*\n\n[Жүктеу]({direct_url})"
                await bot.send_photo(response.from_user.id, thumbnail_url, caption=caption, parse_mode="Markdown")
    elif is_vk_playlist(url):
        await bot.send_message(response.from_user.id, 'Сілтемелер жасалуда...')
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True,
            'format': "url1080/url720/url480/url360/url240/bestvideo[ext=mp4]+bestaudio[ext=mp4]/best[ext=mp4]"
        }
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        info = ydl.extract_info(url, download=False)
        if 'entries' in info:
            playlist_videos = info['entries']
            await bot.send_chat_action(response.chat.id, "upload_video")
            for idx, video in enumerate(playlist_videos, start=1):
                if 'url' in video:
                    video_url = video['url']
                    info_dict = ydl.extract_info(video_url, download=False)
                    if 'url' in info_dict:
                        thumbnail_url = info_dict.get('thumbnail')
                        title = info_dict.get('title', f"Видео {idx}")
                        url_clck = clck.ru(info_dict['url'])
                        caption = f"*@{BOT_USERNAME}*\n\n{title}:\n\n[Жүктеу]({url_clck})\n"
                        await bot.send_photo(response.from_user.id, thumbnail_url, caption=caption, parse_mode="Markdown")
    elif is_vk_wall(url):
        await bot.send_chat_action(response.chat.id, "upload_video")
        command = ['yt-dlp','-F', url]
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout.strip()
        url_pattern = r'\[vk\] Extracting URL: (https://vk\.com/video-[^\s]+)'
        url_match = re.search(url_pattern, output)
        if url_match:
            extracted_url = url_match.group(1)
            try:
                command = ['yt-dlp', '-F', extracted_url]
                result = subprocess.run(command, capture_output=True, text=True)
                output = result.stdout.strip()
                ydl = yt_dlp.YoutubeDL()
                info = ydl.extract_info(extracted_url, download=False)
                with yt_dlp.YoutubeDL() as ydl:
                    info_dict = ydl.extract_info(extracted_url, download=False)
                    if 'url' in info_dict:
                        direct_url = info_dict['url']
                        thumbnail_url = info_dict.get('thumbnail')
                        caption = f"*{info['title']}*\nҰзақтығы: {info['duration'] / 60:.2f} минут \n\n*@{BOT_USERNAME}*\n\n[Жүктеу]({direct_url})"
                        await bot.send_photo(response.from_user.id, thumbnail_url, caption=caption, parse_mode="Markdown")
                    else:
                        await response.reply("URL табылмады. Сілтемені мына форматта жіберіңіз: https://vk.com/video-123457_9101112")
                        await state.clear()
            except Exception as e:
                await response.reply(f"Қате орын алды: {e}")
                await state.clear()
        else:
            await response.reply('Сілтеме VK видеосы ретінде танылмады. Дұрыс сілтеме жіберіңіз.')
            await state.clear()
    else:
        await response.reply('Сілтеме VK видеосы ретінде танылмады. Дұрыс сілтеме жіберіңіз.')
        await state.clear()
