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
db = SQLiter(config.PATH_BASE)

# Обработка комманды /start
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    answer = text('Привет, я помогу найти тебе квартиру для аренды на основе введёной информации',\
             "Для этого воспользуйся командой /find [Мин. цена],[Макс. цена],[Район],[Кол-во комнат],[этаж]",\
             "Например: /find 5000,12000,р-н Калининский,2-комн.,3",     sep='\n')
    await message.answer(answer)

# Обработка комманды /help
@dp.message_handler(commands=["help"])
async def start_command(message: types.Message):
    answer = text("Для того чтобы найти квартиру воспользуйся командой /find [Мин. цена],[Макс. цена],[Район],[Кол-во комнат],[этаж]",\
             "Например: /find 5000,12000,р-н Калининский,2-комн.,3",     sep='\n')
    await message.answer(answer)

# Обновление базы из заранее созданного csv файла
@dp.message_handler(commands=["update_base"])
async def start_command(message: types.Message):
    db.fill_base(csv_file=config.PATH_CSV)
    await message.answer('Ок')

@dp.message_handler(commands=["find"])
async def start_command(message: types.Message):
    arguments = message.get_args()
    if not arguments:
        return await message.reply("Что-то пошло не так")

    arguments = arguments.replace(' ', '')
    arguments = arguments.split(',')

    db.find_in_base(arguments)


    await message.answer("Пук")







@dp.message_handler()
async def echo(message: types.Message):
    await message.reply('Незнаю что с этим делать попробуй воспользоваться коммандами /start или /help')


# @dp.message_handler()
# async def echo(message: types.Message):
#
#     answer = text('Привет, я помогу найти тебе квартиру на основе введёной информации', sep='\n')
#     photo = ["https://cdn-p.cian.site/images/40/455/601/1065540484-1.jpg",
#              "https://cdn-p.cian.site/images/55/670/501/solnechnyy-chelyabinsk-jk-floor-plan-1050765569-6.jpg",
#              "https://cdn-p.cian.site/images/40/455/601/1065540497-1.jpg"]
#     media = []
#     for item in photo:
#         media.append(InputMediaPhoto(item))
#     await bot.send_message(message.from_user.id, answer)
#     await bot.send_media_group(message.from_user.id, media)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)