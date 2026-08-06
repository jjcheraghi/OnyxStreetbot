"""
Onyx Street Telegram Bot (Starter Template)

TODO:
- Replace 8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q
- Replace @Onyx_Street
"""

import telebot
import sqlite3

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"
ADMIN_ID = 8356358583
CHANNEL = "@Onyx_Street"
CHANNEL_LINK = "https://t.me/Onyx_Street"

bot = telebot.TeleBot(TOKEN)

db = sqlite3.connect("onyx.db", check_same_thread=False)
cur = db.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS mods(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT,
 game TEXT,
 photo TEXT,
 description TEXT,
 file_id TEXT,
 downloads INTEGER DEFAULT 0
)
""")
db.commit()

def check_join(user_id):
    try:
        m = bot.get_chat_member(CHANNEL, user_id)
        return m.status in ("member","administrator","creator")
    except:
        return False

@bot.message_handler(commands=["start"])
def start(message):
    if not check_join(message.from_user.id):
        kb=telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton("Join Channel",url=CHANNEL_LINK))
        bot.send_message(message.chat.id,"Please join the channel first.",reply_markup=kb)
        return
    bot.send_message(message.chat.id,"Welcome to Onyx Street!")

print("Bot started")
bot.infinity_polling()

