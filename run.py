import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN_TG
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from handlers import router
from scripts import init_db, add_order_to_db


bot = Bot(token=TOKEN_TG)
dp = Dispatcher()



async def main():
    await init_db()
    await add_order_to_db()
    # await add_db()
    # scheduler = AsyncIOScheduler(timezone="Europe/Minsk")
    # scheduler.add_job(add_db, trigger='interval', minutes=CHECKINTERVAL)
    # scheduler.start()
    dp.include_router(router)
    await dp.start_polling(bot)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filename='py_log.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.debug("A DEBUG Message")
    logging.info("An INFO")
    logging.warning("A WARNING")
    logging.error("An ERROR")
    logging.critical("A message of CRITICAL severity")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')