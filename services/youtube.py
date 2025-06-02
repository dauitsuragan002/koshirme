import re
import yt_dlp
import aiohttp
from aiogram import types
from config_bot import bot, BOT_USERNAME
import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext


def is_youtube_video(url):
    youtube_video_regex = (
        r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/"
        r"(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
    )
    youtube_short_regex = r"https://youtu\.be/([^&=%\?]{11})"
    youtube_shorts_regex = r"https://www\.youtube\.com/shorts/([^&=%\?]+)"
    return (
        re.match(youtube_video_regex, url) is not None
        or re.match(youtube_short_regex, url) is not None
        or re.match(youtube_shorts_regex, url) is not None
    )


def is_youtube_video_clip(url):
    youtube_clip_regex = (
        r"(https?://)?(www\.)?youtube\.com/clip/([^&=%\?]+)"
    )
    return re.match(youtube_clip_regex, url) is not None


async def show_quality_options(message: types.Message, cleaned_url, user_id, state: FSMContext):
    try:
        ydl_opts = {
            'noplaylist': True,
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True,
        }
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        info = ydl.extract_info(cleaned_url, download=False)
        formats = info.get('formats', [])
        desired_resolutions = ['360p', '480p', '720p', '1080p']
        unique_resolutions = set()
        formats_text = "\n".join([f"✅ {f['format_note']}" for f in formats if 'format_note' in f and f['format_note'] in desired_resolutions and (f['format_note'] not in unique_resolutions and unique_resolutions.add(f['format_note']) is None)])
        if formats_text:
            from handlers.download import user_urls
            user_urls[user_id] = cleaned_url
            video_id = info['id']
            thumbnail_formats = ['maxresdefault.jpg', 'hqdefault.jpg', 'mqdefault.jpg', 'sddefault.jpg']
            thumbnail_url = None
            for format in thumbnail_formats:
                formatted_thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/{format}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(formatted_thumbnail_url) as response:
                        if response.status == 200:
                            thumbnail_url = formatted_thumbnail_url
                            break
            if thumbnail_url:
                quality_mapping = {
                    '360p': '605+140',
                    '480p': '135+140',
                    '720p': '22',
                    '1080p': '270+140',
                }
                sorted_resolutions = sorted(unique_resolutions, key=lambda quality: int(quality.split('p')[0]))
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text=f"🎥 {quality}", callback_data=f'download_video_{quality_mapping.get(quality, quality)}') for quality in sorted_resolutions],
                        [InlineKeyboardButton(text='🔊 Аудионы көшіру', callback_data='download_video_140')]
                    ]
                )
                await message.answer_photo(
                    photo=thumbnail_url,
                    caption=f"*{info['title']}*\n\nБейне көлемі: {info['duration'] / 60:.2f} минут\n\n{formats_text} [\n\n@{BOT_USERNAME}]\n\nСапаны таңдаңыз:",
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            else:
                await bot.send_message(user_id, 'Эскиз үшін сурет табылмады.')
            await state.clear()
        else:
            await bot.send_message(user_id, 'YouTube видеосы ретінде танылмады. Дұрыс сілтеме жіберіңіз.')
            await state.clear()
    except Exception as e:
        await bot.send_chat_action(message.chat.id, "upload_video")
        await bot.send_message(user_id, f'Ақпарат жүктеу қатесі: {e}')
        await state.clear()


async def get_youtube_url(response: types.Message, state: FSMContext):
    url = response.text
    cleaned_url = url.split('&list=')[0]
    if is_youtube_video(cleaned_url):
        message_loading = await bot.send_message(response.from_user.id, 'Загружаю информацию про видео...')
        await state.update_data(cleaned_url=cleaned_url)
        await show_quality_options(response, cleaned_url, response.from_user.id, state)
        await bot.delete_message(response.from_user.id, message_loading.message_id)
    else:
        await bot.send_message(response.from_user.id, 'Ссылка не распознана как видео на YouTube. Пожалуйста, введите корректную ссылку.')
        await state.clear()


async def get_youtube_video_clip(response: types.Message, state: FSMContext):
    url = response.text
    cleaned_url = url.split('&list=')[0]
    file_name = None
    if is_youtube_video_clip(cleaned_url):
        await bot.send_chat_action(response.chat.id, "upload_video")
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': f'%(title)s.%(ext)s',
                'noplaylist': True
            }
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            ydl.download([cleaned_url])
            file_name = ydl.prepare_filename(ydl.extract_info(cleaned_url, download=False))
            with open(file_name, 'rb') as video_file:
                await bot.send_video(response.from_user.id, video=video_file, caption='✂️ Вот ваш нарезанный видео!\n\n@koshirme667_bot')
                await state.clear()
        except Exception as e:
            await bot.send_message(response.from_user.id, f"Лимит видео 50 мб: \n{e}")
        finally:
            if file_name:
                import os
                os.remove(file_name)
            await state.clear()
    else:
        await bot.send_message(response.from_user.id, 'Ссылка не распознана как видео на YouTube. Пожалуйста, введите корректную ссылку.')
        await state.clear()
