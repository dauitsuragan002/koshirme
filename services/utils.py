import re, asyncio, aiohttp, io

# --- Жалпы көмекші функциялар ---
def extract_video_link(text):
    url_pattern = r"(https?://[^\s]+)"
    match = re.search(url_pattern, text)
    if match:
        return match.group(0)
    else:
        return None

async def get_video_stream_from_url(direct_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(direct_url) as resp:
            if resp.status == 200:
                video_data = await resp.read()
                return io.BytesIO(video_data)
            else:
                return None

async def get_stream_quality_url(quality_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(quality_url) as resp:
            if resp.status == 200:
                video_data = await resp.read()
                return io.BytesIO(video_data)
            else:
                return None

async def get_thumbinal_quality_url(cleaned_url, ydl):
    try:
        info_dict = ydl.extract_info(cleaned_url, download=False)
        thumbnail_url = info_dict.get('thumbnail')
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    image_stream = io.BytesIO(image_data)
                    return image_stream
    except Exception as e:
        print(f"Error while fetching thumbnail: {e}")
    return None
