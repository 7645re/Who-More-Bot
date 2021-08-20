import asyncio
from random import choices
from vkbottle import KeyboardButtonColor
from vkbottle.exception_factory import VKAPIError
import dbreq

conn = dbreq.create_connection("db.db")
commands = {"balance": {"name": "Баланс", "color": KeyboardButtonColor.POSITIVE, "rank": "user", "type": "default"},
            "profile": {"name": "Профиль", "color": KeyboardButtonColor.PRIMARY, "rank": "user", "type": "default"},
            "commands": {"name": "Команды", "color": KeyboardButtonColor.NEGATIVE, "rank": "user", "type": "default"},
            "WhoMore": {"name": "WhoMore", "color": KeyboardButtonColor.PRIMARY, "rank": "user", "type": "game"}
            }

class WhoMore:
    def __init__(self, name, min, max, loop, bot):
        self.name = name
        self.bank = 0
        self.open = False
        self.members = {}
        self.min = min
        self.max = max
        self.loop = loop
        self.loop.create_task(self.load_backup())
        self.bot = bot

    async def load_backup(self):
        info = await dbreq.get_room_db(conn, self.name)
        if info:
            for room_bet in info:
                self.members[room_bet[0]] = room_bet[2]
                self.bank += room_bet[2]
            print(f"load backup for {self.name}")
        if len(self.members) >= 2:
            await self.choose_winer(0)
        self.open = True
    
    async def clear_backup(self):
        self.open = False
        info = await dbreq.get_room_db(conn, self.name)
        if info:
            await dbreq.del_room_db(conn, self.name)
            print(f"clear backup for {self.name}")
        self.open = True

    async def deposite(self, user_id, money):
        if self.open and money.isdigit() and int(money) <= self.max and int(money)>= self.min and\
            (self.members[user_id] if user_id in self.members else 0)  + int(money) <= self.max:
            self.open = False
            money = int(money)
            deposite_access = await dbreq.subtract_user_balance(conn, user_id, money)
            if deposite_access:
                if user_id in self.members:
                    self.members[user_id] += money
                else:
                    self.members[user_id] = money
                self.bank += money
                await dbreq.add_user_bet(conn, self.name, user_id, money)

                if len(self.members) >= 2:
                    self.loop.create_task(self.choose_winer(10))
                self.open = True
                return "Операция прошла успешно!"
        else:
            return "Во время совершения операции произошла ошибка..."
    
    async def withdraw(self, user_id):
        if self.open and user_id in self.members:
            self.open = False
            await dbreq.add_user_balance(conn, user_id, self.members[user_id])
            await dbreq.del_user_bet(conn, self.name, user_id)
            del self.members[user_id]
            self.open = True
            return f"Возврат средств был осуществлён!"
        return f"Возврат средств не был осуществлён!"

    async def choose_winer(self, sec):
        await asyncio.sleep(sec)
        if len(self.members) >= 2:
            self.open = False
            winner = choices([name for name in self.members],
            weights=[self.members[name] for name in self.members])[0]
            message = f"[id{winner}|Победитель] выйграл {self.bank}"
            await self.notifire(message)
            await dbreq.add_user_balance(conn, winner, self.bank)
            await dbreq.del_room_db(conn, self.name)
            self.bank = 0
            self.members = {}
            self.open = True
    
    async def notifire(self, message):
        for user_id in self.members:
            try:
                await self.bot.api.messages.send(peer_id=user_id, message=message, random_id=0)
            except VKAPIError(901):
                print(f"Ошибка отправки сообщения пользователю id{user_id}")

async def balance(user_id):
    return await dbreq.get_user_balance(conn, user_id)

async def profile(user_id):
    result = await dbreq.get_user_profile(conn, user_id)
    message = f"Имя: {result[0]}\nБаланс: {result[1]}$\nПобеды: {result[2]}\nПроигрыши: {result[3]}\nПроцент побед: {result[4]}"
    return message

async def convert_members(room):
    result = ""
    i = 1
    for user_id in room:
        result += f"[id{user_id}|Игрок {i}] поставил {room[user_id]}$\n"
        i+=1
    return result