from aiogram import types
from config_bot import dp, bot, user_urls
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from services.utils import extract_video_link
from services.youtube import show_quality_options, is_youtube_video, is_youtube_video_clip, get_youtube_url, get_youtube_video_clip
from services.utils import get_stream_quality_url, get_thumbinal_quality_url
from services.vk import is_vk_video, is_vk_wall, is_vk_playlist, get_direct_video_url
from services.tiktok import is_tiktok_video, get_tiktok_url
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Filter
from aiogram import Router
from services.instagram import is_instagram_video, get_instagram_url

router = Router()

class DownloadStates(StatesGroup):
    waiting_for_youtube_url = State()
    waiting_for_vk_url = State()
    waiting_for_tt_url = State()
    waiting_for_ig_url = State()

@router.callback_query(lambda callback_query: callback_query.data in ['youtube', 'вконтакте', 'tiktok', 'instagram'])
async def get_service(callback_query: types.CallbackQuery, state: FSMContext):
    service = callback_query.data
    if service == 'youtube':
        await callback_query.message.reply('YouTube видеосының сілтемесін енгізіңіз', reply_markup=types.ForceReply())
        await state.set_state(DownloadStates.waiting_for_youtube_url)
    elif service == 'вконтакте':
        await callback_query.message.reply('ВКонтакте видеосының сілтемесін енгізіңіз', reply_markup=types.ForceReply())
        await state.set_state(DownloadStates.waiting_for_vk_url)
    elif service == 'tiktok':
        await callback_query.message.reply('TikTok видеосының сілтемесін енгізіңіз', reply_markup=types.ForceReply())
        await state.set_state(DownloadStates.waiting_for_tt_url)
    elif service == 'instagram':
        await callback_query.message.reply('Instagram видеосының сілтемесін енгізіңіз', reply_markup=types.ForceReply())
        await state.set_state(DownloadStates.waiting_for_ig_url)
    else:
        await callback_query.message.reply('Қате сервис таңдауы. Түйменің бірін басыңыз.')

@dp.message(lambda message: extract_video_link(message.text))
async def process_video_link(message: types.Message, state: FSMContext):
    await bot.send_chat_action(message.chat.id, "typing")
    await bot.delete_message(message.chat.id, message.message_id)
    url = extract_video_link(message.text)
    if url:
        if is_youtube_video(url):
            await get_youtube_url(message, state)
        elif is_youtube_video_clip(url):
            await get_youtube_video_clip(message, state)
        elif is_tiktok_video(url):
            await get_tiktok_url(message, state)
        elif is_vk_video(url):
            await get_direct_video_url(message, state)
        elif is_vk_wall(url):
            await get_direct_video_url(message, state)
        elif is_vk_playlist(url):
            await get_direct_video_url(message, state)
        elif is_instagram_video(url):
            await get_instagram_url(message, state)
        else:
            await message.answer("🔗Тек YouTube, Instagram немесе ВКонтакте сілтемесін жіберіңіз.")
    else:
        error_message = await bot.send_message(message.chat.id, "🔗Тек YouTube, Instagram немесе ВКонтакте сілтемесін жіберіңіз.")
        await asyncio.sleep(7)
        await bot.delete_message(chat_id=error_message.chat.id, message_id=error_message.message_id)

@router.callback_query(lambda callback_query: callback_query.data.startswith('download_video'))
async def download_video_callback(callback_query: types.CallbackQuery, state: FSMContext):
    selected_quality = callback_query.data.replace('download_video_', '').lower()
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    file_name = None
    user_id = callback_query.from_user.id
    cleaned_url = user_urls.get(user_id)
    try:
        if is_youtube_video(cleaned_url):
            if selected_quality == '605+140' or selected_quality == '135+140' or selected_quality == '270+140':
                await bot.send_chat_action(callback_query.message.chat.id, "upload_video")
                import yt_dlp
                ydl_opts = {
                    'format': selected_quality,
                    'outtmpl': f'%(title)s.%(ext)s',
                    'noplaylist': True,
                    'quiet': True
                }
                ydl = yt_dlp.YoutubeDL(ydl_opts)
                ydl.download([cleaned_url])
                file_name = ydl.prepare_filename(ydl.extract_info(cleaned_url, download=False))
                with open(file_name, 'rb') as video_file:
                    await bot.send_video(user_id, video=video_file, caption='Вот ваше видео!\n\n@koshirme667_bot')
            elif selected_quality == '22':
                await bot.send_chat_action(callback_query.message.chat.id, "upload_video")
                import yt_dlp
                ydl_opts = {
                    'format': '22',
                    'outtmpl': f'%(title)s.%(ext)s',
                    'noplaylist': True,
                    'quiet': True
                }
                video_stream = None
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(cleaned_url, download=False)
                    if 'url' in info_dict:
                        quality_url = info_dict['url']
                        video_stream = await get_stream_quality_url(quality_url)
                if video_stream:
                    await bot.send_video(user_id, video=video_stream, caption='Вот ваше видео!\n\n@koshirme667_bot')
            elif selected_quality == '140':
                await bot.send_chat_action(callback_query.message.chat.id, "upload_audio")
                import yt_dlp
                ydl_opts = {
                    'format': selected_quality,
                    'outtmpl': f'%(title)s.%(ext)s',
                    'noplaylist': True,
                    'quiet': True
                }
                ydl = yt_dlp.YoutubeDL(ydl_opts)
                ydl.download([cleaned_url])
                file_name = ydl.prepare_filename(ydl.extract_info(cleaned_url, download=False))
                image_stream = await get_thumbinal_quality_url(cleaned_url, ydl)
                with open(file_name, 'rb') as audio_file:
                    await bot.send_audio(user_id, audio=audio_file, thumb=image_stream, caption='Вот ваше видео!\n\n@koshirme667_bot')
            else:
                await bot.send_message(user_id, 'Сілтеме YouTube видеосы ретінде танылмады. Дұрыс сілтеме жіберіңіз.')
                await state.clear()
            if file_name:
                import os
                os.remove(file_name)
    except Exception as e:
        if file_name:
            import os
            os.remove(file_name)
        error_message = await bot.send_message(user_id, 'Таңдалған сапада видео жоқ')
        await asyncio.sleep(5)
        await bot.delete_message(chat_id=error_message.chat.id, message_id=error_message.message_id)
        print(f"Видео жүктеу және жіберу кезінде қате: {e}")
