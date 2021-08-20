import asyncio
from typing import Optional
from vkbottle.bot import Bot, Message
from datetime import datetime
from vkbottle.tools.dev_tools import keyboard
import commands
import keyboards
from config import get_token


start_time = datetime.now()
bot = Bot(get_token("token.txt"))
event_loop = asyncio.get_event_loop()
WhoMore_rooms = {"1_flor": commands.WhoMore(name="1_flor", min=50, max=110, loop=event_loop, bot=bot), 
                "2_flor": commands.WhoMore(name="2_flor", min=110, max=160, loop=event_loop, bot=bot),
                "3_flor": commands.WhoMore(name="3_flor", min=160, max=210, loop=event_loop, bot=bot)}


@bot.on.message(text="Баланс")
async def handler(message: Message):
    balance = await commands.balance(message.from_id)
    await message.answer(message=f"Ваш баланс: {balance}$", 
    keyboard=keyboards.commands_keyboard())

@bot.on.message(text=["Начать", "Команды"])
async def handler(message: Message):
    await message.answer(message="Список доступных комманд представлен во встроенной клавиатуре",
    keyboard=keyboards.commands_keyboard())

@bot.on.message(text="Профиль")
async def handler(message: Message):
    user_profile = await commands.profile(message.from_id)
    await message.answer(message=user_profile,
    keyboard=keyboards.commands_keyboard())

@bot.on.message(text="WhoMore")
async def handler(message: Message):
    await message.answer("Игра называется WhoMore, выигрывает случайный человек, но можно увеличить свои шансы на победу"
    + ",поставив большую сумму.", keyboard=keyboards.whomore_rooms_keyboard(WhoMore_rooms))

@bot.on.message(text=[room for room in WhoMore_rooms])
async def handler(message: Message):
    await message.answer(message=f"Информация по комнате {message.text}\nБанк: {WhoMore_rooms[message.text].bank}\n"+
    f"Мин.Ставка: {WhoMore_rooms[message.text].min}\nМакс.Ставка: {WhoMore_rooms[message.text].max}\n"+
    f"Участники: \n{await commands.convert_members(WhoMore_rooms[message.text].members)}\n" + 
    f"Состояние комнаты: {'Открыта' if WhoMore_rooms[message.text].open else 'Закрыта'}\n" +\
    f"Команда, чтобы сделать свою ставку: {message.text} число",
    keyboard=keyboards.whomore_room_keyboard(WhoMore_rooms[message.text]))

@bot.on.message(text=[room +" withdraw" for room in WhoMore_rooms])
async def handler(message: Message):
    operation_result = await WhoMore_rooms[message.text.split(" ")[0]].withdraw(message.from_id)
    room_name = message.text.split(' ')[0]
    await message.answer(operation_result)
    await message.answer(message=f"Информация по комнате {room_name}\nБанк: {WhoMore_rooms[room_name].bank}\n"+
    f"Мин.Ставка: {WhoMore_rooms[room_name].min}\nМакс.Ставка: {WhoMore_rooms[room_name].max}\n"+
    f"Участники: \n{await commands.convert_members(WhoMore_rooms[room_name].members)}\n" +
    f"Состояние комнаты: {'Открыта' if WhoMore_rooms[room_name].open else 'Закрыта'}",
    keyboard=keyboards.whomore_rooms_keyboard(WhoMore_rooms))

@bot.on.message(text=[room +" <bet>" for room in WhoMore_rooms])
async def handler(message: Message, bet: Optional[int]):
    room_name = message.text.split(' ')[0]
    operation_result = await WhoMore_rooms[room_name].deposite(message.from_id, bet)
    await message.answer(operation_result)
    await message.answer(message=f"Информация по комнате {room_name}\nБанк: {WhoMore_rooms[room_name].bank}\n"+
    f"Мин.Ставка: {WhoMore_rooms[room_name].min}\nМакс.Ставка: {WhoMore_rooms[room_name].max}\n"+
    f"Участники: \n{await commands.convert_members(WhoMore_rooms[room_name].members)}\n" +
    f"Состояние комнаты: {'Открыта' if WhoMore_rooms[room_name].open else 'Закрыта'}",
    keyboard=keyboards.whomore_rooms_keyboard(WhoMore_rooms))


print(datetime.now()-start_time)
bot.run_forever()