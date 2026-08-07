import telebot
from telebot import types
import sqlite3

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"

ADMIN_ID = 8356358583
CHANNEL = "@Onyx_Street"
BOT_USERNAME = "OnyxStreetbot"

bot = telebot.TeleBot(TOKEN)

DB = "mods.db"
admin_state = {}


# DATABASE

def connect():
    return sqlite3.connect(DB)


def setup_db():
    con = connect()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS mods(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        type TEXT,
        file_id TEXT,
        url TEXT
    )
    """)

    con.commit()
    con.close()


setup_db()



# HELPERS

def is_admin(uid):
    return uid == ADMIN_ID



def is_joined(uid):

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



def join_keyboard():

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "Join Channel",
            url=f"https://t.me/{CHANNEL.replace('@','')}"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "Verify",
            callback_data="verify"
        )
    )

    return kb



# START

@bot.message_handler(commands=["start"])
def start(message):

    args = message.text.split()

    if len(args) > 1:

        if not is_joined(
            message.from_user.id
        ):

            bot.send_message(
                message.chat.id,
                "Join channel first.",
                reply_markup=join_keyboard()
            )
            return


        send_mod(
            message.chat.id,
            args[1]
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

    if is_joined(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "Verified"
        )

    else:

        bot.answer_callback_query(
            call.id,
            "Not joined"
        )



# ADMIN PANEL

@bot.message_handler(commands=["admin"])
def admin_panel(message):

    if not is_admin(
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
            "List Mods",
            callback_data="list"
        )
    )


    bot.send_message(
        message.chat.id,
        "Admin Panel",
        reply_markup=kb
    )



# ADD MOD

@bot.callback_query_handler(
    func=lambda c:c.data=="add"
)
def add_mod(call):

    admin_state[
        call.from_user.id
    ] = "name"


    bot.send_message(
        call.message.chat.id,
        "Send mod name:"
    )



@bot.message_handler(
    func=lambda m:
    is_admin(m.from_user.id)
    and admin_state.get(m.from_user.id)=="name"
)
def get_name(message):

    admin_state[
        message.from_user.id
    ] = {
        "name":message.text,
        "step":"file"
    }


    bot.send_message(
        message.chat.id,
        "Send file or link:"
    )
