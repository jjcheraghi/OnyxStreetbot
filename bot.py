import telebot
import sqlite3
import random

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"

ADMIN_ID = 8356358583

bot = telebot.TeleBot(TOKEN)

db = sqlite3.connect("links.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY,
    url TEXT
)
""")
db.commit()


@bot.message_handler(commands=["start"])
def start(message):
    args = message.text.split()

    if len(args) > 1:
        code = args[1]

        cursor.execute("SELECT url FROM links WHERE id=?", (code,))
        result = cursor.fetchone()

        if result:
            bot.send_message(
                message.chat.id,
                f"📦 لینک دانلود مود:\n\n{result[0]}"
            )
        else:
            bot.send_message(message.chat.id, "❌ لینک پیدا نشد")
    else:
        bot.send_message(message.chat.id, "سلام 👋")


@bot.message_handler(commands=["add"])
def add_link(message):
    if message.from_user.id != ADMIN_ID:
        return

    url = message.text.replace("/add ", "")

    cursor.execute(
        "INSERT INTO links(url) VALUES(?)",
        (url,)
    )

    db.commit()

    code = cursor.lastrowid

    bot.send_message(
        message.chat.id,
        f"✅ ذخیره شد\n\nلینک دانلود:\nhttps://t.me/OnyxStreetBot?start={code}"
    )


bot.infinity_polling()
