import telebot
from telebot import types
import sqlite3

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"

ADMIN_ID = 8356358583
CHANNEL = "@Onyx_Street"
BOT_USERNAME = "OnyxStreetbot"

bot = telebot.TeleBot(TOKEN)

DB = "mods.db"
state = {}


def db():
    return sqlite3.connect(DB)


def setup():

    con = db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS mods(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        photo TEXT,
        type TEXT,
        file_id TEXT,
        url TEXT
    )
    """)

    con.commit()
    con.close()


setup()



def admin(uid):
    return uid == ADMIN_ID



def check_join(uid):

    try:
        member = bot.get_chat_member(
            CHANNEL,
            uid
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:
        return False



def join_kb():

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "Join Channel",
            url=f"https://t.me/{CHANNEL.replace('@','')}"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "I Joined",
            callback_data="verify"
        )
    )

    return kb



@bot.message_handler(commands=["start"])
def start(message):

    args = message.text.split()

    if len(args) > 1:

        if not check_join(
            message.from_user.id
        ):

            bot.send_message(
                message.chat.id,
                "Join the channel first.",
                reply_markup=join_kb()
            )
            return


        send_mod(
            message.chat.id,
            int(args[1])
        )

        return


    bot.send_message(
        message.chat.id,
        "Welcome to ONYX STREET"
    )



@bot.callback_query_handler(
    func=lambda c:c.data=="verify"
)
def verify(call):

    if check_join(
        call.from_user.id
    ):

        bot.answer_callback_query(
            call.id,
            "Verified"
        )

        bot.send_message(
            call.message.chat.id,
            "Now open the mod link."
        )

    else:

        bot.answer_callback_query(
            call.id,
            "Not joined yet"
        )



@bot.message_handler(commands=["admin"])
def admin_panel(message):

    if not admin(
        message.from_user.id
    ):
        return


    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "Add Mod",
            callback_data="add"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "Delete Mod",
            callback_data="delete"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "My Mods",
            callback_data="list"
        )
    )


    bot.send_message(
        message.chat.id,
        "Admin Panel",
        reply_markup=kb
    )



@bot.callback_query_handler(
    func=lambda c:c.data=="add"
)
def add_start(call):

    state[call.from_user.id] = {
        "step":"name"
    }

    bot.send_message(
        call.message.chat.id,
        "Send mod name:"
    )



@bot.message_handler(
    func=lambda m:
    admin(m.from_user.id)
    and m.from_user.id in state
    and state[m.from_user.id]["step"]=="name"
)
def get_name(message):

    state[message.from_user.id]["name"] = message.text

    state[message.from_user.id]["step"] = "photo"

    bot.send_message(
        message.chat.id,
        "Send cover image or type skip:"
    )



@bot.message_handler(
    content_types=["photo"]
)
def get_photo(message):

    if message.from_user.id not in state:
        return

    state[message.from_user.id]["photo"] = message.photo[-1].file_id

    state[message.from_user.id]["step"] = "file"

    bot.send_message(
        message.chat.id,
        "Send file or link:"
    )
