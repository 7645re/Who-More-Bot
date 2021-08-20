import sqlite3
from sqlite3.dbapi2 import Error

from vkbottle.tools.dev_tools.auth._flows import user


def create_connection(db_file):
  conn = None
  try:
    conn = sqlite3.connect(db_file)
  except Error as e:
    print(e)
  return conn


async def check_profile_exist(conn, user_id):
    cur = conn.cursor()
    result = cur.execute(f"SELECT * FROM users WHERE id={user_id}").fetchall()
    if not result:
        cur.execute(f"INSERT INTO users VALUES ({user_id}, 2000, 0, 0, 0)")
        conn.commit()

async def get_user_balance(conn, user_id):
    cur = conn.cursor()
    await check_profile_exist(conn, user_id)
    return cur.execute(f"SELECT balance FROM users WHERE id={user_id}").fetchall()[0][0]

async def get_user_profile(conn, user_id):
    cur = conn.cursor()
    await check_profile_exist(conn, user_id)
    return cur.execute(f"SELECT * FROM users WHERE id={user_id}").fetchall()[0]

async def subtract_user_balance(conn, user_id, subtract_amount):
    cur = conn.cursor()
    await check_profile_exist(conn, user_id)
    user_balance = cur.execute(f"SELECT balance FROM users WHERE id={user_id}").fetchall()[0][0]
    if user_balance >= subtract_amount:
        cur.execute(f"UPDATE users SET balance = {user_balance-subtract_amount} WHERE id={user_id}")
        conn.commit()
        return True
    else:
        return False

async def add_user_balance(conn, user_id, additional_amount):
    cur = conn.cursor()
    await check_profile_exist(conn, user_id)
    user_balance = cur.execute(f"SELECT balance FROM users WHERE id={user_id}").fetchall()[0][0]
    cur.execute(f"UPDATE users SET balance = {user_balance+additional_amount} WHERE id={user_id}")
    conn.commit()
  
async def add_user_bet(conn, room_name, user_id, bet):
    cur = conn.cursor()
    result = cur.execute(f"SELECT bet FROM WhoMore WHERE id={user_id} AND room_name='{room_name}'").fetchall()
    if not result:
        cur.execute(f"INSERT INTO WhoMore VALUES ({user_id}, '{room_name}', {bet})")
    else:
        cur.execute(f"UPDATE WhoMore SET bet = {result[0][-1]+bet} WHERE id={user_id}")
    conn.commit()

async def del_user_bet(conn, room_name, user_id):
    cur = conn.cursor()
    result = cur.execute(f"SELECT bet FROM WhoMore WHERE id={user_id} AND room_name='{room_name}'").fetchall()
    if result:
        cur.execute(f"DELETE FROM WhoMore WHERE id={user_id} AND room_name='{room_name}'")
        conn.commit()

async def get_room_db(conn, room_name):
    cur = conn.cursor()
    return cur.execute(f"SELECT * FROM WhoMore WHERE room_name='{room_name}'").fetchall()

async def del_room_db(conn, room_name):
    cur = conn.cursor()
    cur.execute(f"DELETE FROM WhoMore WHERE room_name='{room_name}'")
    conn.commit()