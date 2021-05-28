import config
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputMediaPhoto, InputTextMessageContent
from aiogram.utils.markdown import text
from sqliter import SQLiter

#Задаем уровень логов
logging.basicConfig(level=logging.INFO)

# Инициализируем бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

# Инициализируем соединение с БД
db = SQLiter('.//data/dbFlat.db')

# Эхо метод
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    answer = text('Привет, я помогу найти тебе квартиру на основе введёной информации', sep='\n')
    await message.answer(answer)

@dp.message_handler(commands=["update_base"])
async def start_command(message: types.Message):
    SQLiter.fill_base(csv_file='.//data/flats.csv')
    await message.answer('Привет')

@dp.message_handler()
async def echo(message: types.Message):

    answer = text('Привет, я помогу найти тебе квартиру на основе введёной информации', sep='\n')
    photo = ["https://cdn-p.cian.site/images/40/455/601/1065540484-1.jpg",
             "https://cdn-p.cian.site/images/55/670/501/solnechnyy-chelyabinsk-jk-floor-plan-1050765569-6.jpg",
             "https://cdn-p.cian.site/images/40/455/601/1065540497-1.jpg"]
    media = []
    for item in photo:
        media.append(InputMediaPhoto(item))
    await bot.send_message(message.from_user.id, answer)
    await bot.send_media_group(message.from_user.id, media)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)