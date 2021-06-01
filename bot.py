import config
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputMediaPhoto, InputTextMessageContent
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import text
from asyncio import sleep
from sqliter import SQLiter


class States(StatesGroup):
    """
    class for set up state user
    """
    min = State()
    max = State()
    district = State()
    rooms = State()
    flor = State()
    finish = State()


# Задаем уровень логов
logging.basicConfig(level=logging.INFO)

# Инициализируем бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Инициализируем соединение с БД
db = SQLiter(config.PATH_BASE)


@dp.message_handler(commands=["start"], state="*")
async def start_command(message: types.Message):
    answer = text('Привет, я помогу найти тебе квартиру для аренды на основе введёной информации', \
                  "Параметры по которым ведётся поиск: Мин. цена, Макс. цена, Район, Кол-во комнат, Этаж", \
                  "Давайте начнем. \nВведите начальную стоимость аренды. Например: 5000", sep='\n')
    await message.answer(answer)
    await States.min.set()


# Обработка комманды /help
@dp.message_handler(commands=["help"], state="*")
async def help_command(message: types.Message):
    answer = text("Для того чтобы найти квартиру воспользуйся командой /find ",
                  "Параметры по которым ведётся поиск: Мин. цена, Макс. цена, Район, Кол-во комнат, Этаж", sep='\n')
    await message.answer(answer)


# Обновление базы из заранее созданного csv файла
@dp.message_handler(commands=["update_base"], state="*")
async def update_base_command(message: types.Message):
    db.fill_base(csv_file=config.PATH_CSV)
    await message.answer('Ок')


@dp.message_handler(commands=["find"], state="*")
async def find_command(message: types.Message):
    answer = text("Введите начальную стоимость аренды. Например: 5000", sep='\n')
    await message.answer(answer)
    await States.min.set()


@dp.message_handler(state=States.min)
async def min_command(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста введите число")
        return

    await state.update_data(min_price=message.text)
    await States.next()
    await message.answer("Введите максимальную стоимость аренды. Например: 12000")


@dp.message_handler(state=States.max)
async def max_command(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста введите число")
        return

    await state.update_data(max_price=message.text)
    await States.next()
    await message.answer("Введите Район. Например: Калининский")


@dp.message_handler(state=States.district)
async def district_command(message: types.Message, state: FSMContext):
    await state.update_data(district=message.text)
    await States.next()
    await message.answer("Введите кол-во комнат. Например: 2")


@dp.message_handler(state=States.rooms)
async def rooms_command(message: types.Message, state: FSMContext):
    await state.update_data(rooms=message.text)
    await States.next()
    await message.answer("Введите этаж. Например: 3")


@dp.message_handler(state=States.flor)
async def flor_command(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста введите число")
        return

    await state.update_data(flor=message.text)
    user_data = await state.get_data()

    result = db.find_in_base(user_data)
    if len(result) == 0:
        await message.answer("В нашей базе нет подходящих вариантов :(")
        await States.next()
        return

    for flat in result:
        if flat[10] == '':
            await message.answer(text(f"{flat[0]}, {flat[1]}, {flat[2]}, {flat[3]}, дом {flat[4]}, площадь {flat[5]},"
                                      f"Этаж {flat[6]}, Тип квартиры {flat[7]}, Цена {flat[8]} в месяц, {flat[9]}"))
            await sleep(1)

        else:
            media = []
            media.append(InputMediaPhoto(flat[10], text(
                f"{flat[0]}, {flat[1]}, {flat[2]}, {flat[3]}, дом {flat[4]}, площадь {flat[5]},"
                f"Этаж {flat[6]}, Тип квартиры {flat[7]}, Цена {flat[8]} в месяц, {flat[9]}")))
            await bot.send_media_group(message.from_user.id, media)
            await sleep(1)
    await States.next()


@dp.message_handler(state=States.finish)
async def finish_command(message: types.Message):
    await message.answer("Если хотите начать новый поиск напишите команду /find")


@dp.message_handler()
async def echo(message: types.Message):
    await message.reply('Незнаю что с этим делать попробуй воспользоваться коммандами /start или /help')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
