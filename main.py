import asyncio

from config_bot import dp, bot
from aiogram.filters import Command
from handlers.commands import *
from handlers.download import router as download_router

dp.message.register(start_handler, Command('start'))
dp.message.register(info_handler, Command('info'))
dp.message.register(more_handler, Command('more'))
dp.message.register(help_handler, Command('help'))
dp.message.register(download_handler, Command('download'))
dp.include_router(download_router)

async def main():
    try:
        print('Update successfully!')
        await dp.start_polling(bot)
    except Exception as e:
        print("Expaction accurated:",e)

if __name__ == '__main__':
    asyncio.run(main())