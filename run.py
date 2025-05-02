import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN_TG, CHECKINTERVAL, CHECKINTERVALR
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from handlers import router
from scripts import init_db, add_order_to_db, rassilka_full, check_del_password_db


bot = Bot(token=TOKEN_TG)
dp = Dispatcher()



async def main():
    await init_db()
    await add_order_to_db()
    scheduler = AsyncIOScheduler(timezone="Europe/Minsk")
    scheduler.add_job(rassilka_full, trigger='interval', seconds=CHECKINTERVALR,
                      kwargs={
                          'bot': bot,
                      }
                      )
    scheduler.add_job(add_order_to_db, trigger='interval', seconds=CHECKINTERVAL)
    scheduler.add_job(check_del_password_db, trigger='interval', seconds=CHECKINTERVAL)


    scheduler.start()
    dp.include_router(router)
    await dp.start_polling(bot)



if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING, filename='py_log.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.warning("A WARNING")
    logging.error("An ERROR")
    logging.critical("A message of CRITICAL severity")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.error('Exit')