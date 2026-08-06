import telebot
import sqlite3

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"

ADMIN_ID = 8356358583

CHANNEL = "@Onyx_Street"
CHANNEL_LINK = "https://t.me/Onyx_Street"

bot = telebot.TeleBot(TOKEN)


db = sqlite3.connect("onyx.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS mods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    game TEXT,
    link TEXT
)
""")

db.commit()


def check_join(user_id):
    try:
        member = bot.get_chat_member(
            CHANNEL,
            user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:
        return False



def menu():

    kb = telebot.types.InlineKeyboardMarkup()

    kb.add(
        telebot.types.InlineKeyboardButton(
            "🔥 مودها",
            callback_data="mods"
        )
    )

    kb.add(
        telebot.types.InlineKeyboardButton(
            "📢 کانال",
            url=CHANNEL_LINK
        )
    )

    return kb



def join_menu():

    kb = telebot.types.InlineKeyboardMarkup()

    kb.add(
        telebot.types.InlineKeyboardButton(
            "📢 عضویت",
            url=CHANNEL_LINK
        )
    )

    kb.add(
        telebot.types.InlineKeyboardButton(
            "✅ بررسی",
            callback_data="check"
        )
    )

    return kb



@bot.message_handler(commands=["start"])
def start(message):

    if not check_join(message.from_user.id):

        bot.send_message(
            message.chat.id,
            "⚠️ ابتدا عضو کانال شوید",
            reply_markup=join_menu()
        )

        return


    bot.send_message(
        message.chat.id,
        """
🚗 Onyx Street

خوش آمدید 👋

از منو استفاده کنید:
""",
        reply_markup=menu()
    )



@bot.callback_query_handler(
    func=lambda c:c.data=="check"
)
def check(c):

    if check_join(c.from_user.id):

        bot.answer_callback_query(
            c.id,
            "عضویت تایید شد ✅"
        )

        bot.send_message(
            c.message.chat.id,
            "حالا /start بزن"
        )

    else:

        bot.answer_callback_query(
            c.id,
            "عضو نیستید ❌"
        )



@bot.callback_query_handler(
    func=lambda c:c.data=="mods"
)
def mods(c):

    cursor.execute(
        "SELECT id,name,game FROM mods"
    )

    data = cursor.fetchall()


    if not data:

        bot.send_message(
            c.message.chat.id,
            "❌ هنوز مود ثبت نشده"
        )

        return


    text = "🔥 مودها:\n\n"

    for x in data:

        text += f"""
🚗 {x[1]}
🎮 {x[2]}

/mod{x[0]}
"""


    bot.send_message(
        c.message.chat.id,
        text
    )



@bot.message_handler(commands=["mod"])
def mod(message):

    mid = message.text.replace(
        "/mod",
        ""
    )

    cursor.execute(
        "SELECT name,game,link FROM mods WHERE id=?",
        (mid,)
    )

    x = cursor.fetchone()


    if x:

        bot.send_message(
            message.chat.id,
            f"""
🚗 {x[0]}

🎮 {x[1]}

⬇️ دانلود:
{x[2]}
"""
        )

    else:

        bot.send_message(
            message.chat.id,
            "❌ پیدا نشد"
        )



@bot.message_handler(commands=["add"])
def add(message):

    if message.from_user.id != ADMIN_ID:
        return


    text = message.text.split("|")


    if len(text) != 4:

        bot.send_message(
            message.chat.id,
            """
فرمت:

/add | اسم مود | بازی | لینک
"""
        )

        return


    cursor.execute(
        """
        INSERT INTO mods
        (name,game,link)
        VALUES(?,?,?)
        """,
        (
            text[1],
            text[2],
            text[3]
        )
    )

    db.commit()


    bot.send_message(
        message.chat.id,
        "✅ مود اضافه شد"
    )



@bot.message_handler(commands=["admin"])
def admin(message):

    if message.from_user.id == ADMIN_ID:

        bot.send_message(
            message.chat.id,
            """
🛠 پنل ادمین

افزودن مود:

/add | اسم | بازی | لینک
"""
        )



print("Onyx Street Bot Running")

bot.infinity_polling()
