from vkbottle import Keyboard, Text, KeyboardButtonColor
from vkbottle.tools.dev_tools.vkscript_converter.definitions import attribute
from commands import commands


def commands_keyboard():
    i = 0
    commands_keyboards = Keyboard(one_time=True, inline=False)
    for command in commands:
        if commands[command]["rank"] == "user":
            commands_keyboards.add(Text(commands[command]["name"]), color=commands[command]["color"])
            if i == 2:
                commands_keyboards.row()
        i+=1
    return commands_keyboards

def whomore_rooms_keyboard(rooms):
    whomore_keyboard = Keyboard(one_time=False, inline=False)
    for room in rooms:
        whomore_keyboard.add(Text(room))
    whomore_keyboard.row()
    for room in rooms:
        whomore_keyboard.add(Text(f"{room} withdraw"))
    return whomore_keyboard.row().add(Text("Команды"), color=KeyboardButtonColor.NEGATIVE)

def whomore_room_keyboard(room):
    whomore_room_keyboard = Keyboard(inline=True)
    bet = room.min
    for i in range(6):
        if bet <= room.max:
            whomore_room_keyboard.add(Text(f"{room.name} {bet}"))
            if i == 2:
                whomore_room_keyboard.row()
            bet+=(room.max-room.min)//6
    return whomore_room_keyboard