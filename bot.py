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
# SAVE FILE

@bot.message_handler(
    content_types=["document"]
)
def save_file(message):

    if not is_admin(
        message.from_user.id
    ):
        return

    data = admin_state.get(
        message.from_user.id
    )

    if not isinstance(data, dict):
        return


    con = connect()
    cur = con.cursor()

    cur.execute(
        """
        INSERT INTO mods
        (name,type,file_id)
        VALUES (?,?,?)
        """,
        (
            data["name"],
            "file",
            message.document.file_id
        )
    )

    mod_id = cur.lastrowid

    con.commit()
    con.close()


    del admin_state[
        message.from_user.id
    ]


    link = (
        f"https://t.me/"
        f"{BOT_USERNAME}"
        f"?start={mod_id}"
    )


    bot.send_message(
        message.chat.id,
        f"Mod Added\n\n{link}"
    )



# SAVE LINK

@bot.message_handler(
    func=lambda m:
    is_admin(m.from_user.id)
    and isinstance(
        admin_state.get(m.from_user.id),
        dict
    )
    and admin_state[m.from_user.id]["step"]=="file"
)
def save_link(message):

    data = admin_state[
        message.from_user.id
    ]


    con = connect()
    cur = con.cursor()

    cur.execute(
        """
        INSERT INTO mods
        (name,type,url)
        VALUES (?,?,?)
        """,
        (
            data["name"],
            "link",
            message.text
        )
    )

    mod_id = cur.lastrowid

    con.commit()
    con.close()


    del admin_state[
        message.from_user.id
    ]


    link = (
        f"https://t.me/"
        f"{BOT_USERNAME}"
        f"?start={mod_id}"
    )


    bot.send_message(
        message.chat.id,
        f"Mod Added\n\n{link}"
    )



# SEND MOD

def send_mod(chat_id, mod_id):

    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT * FROM mods WHERE id=?",
        (mod_id,)
    )

    mod = cur.fetchone()

    con.close()


    if not mod:

        bot.send_message(
            chat_id,
            "Not found"
        )

        return


    if mod[2] == "file":

        bot.send_document(
            chat_id,
            mod[3]
        )

    else:

        kb = types.InlineKeyboardMarkup()

        kb.add(
            types.InlineKeyboardButton(
                "Download",
                url=mod[4]
            )
        )

        bot.send_message(
            chat_id,
            "Download:",
            reply_markup=kb
        )



# LIST

@bot.callback_query_handler(
    func=lambda c:c.data=="list"
)
def list_mods(call):

    if not is_admin(call.from_user.id):
        return


    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT id,name FROM mods"
    )

    mods = cur.fetchall()

    con.close()


    text = "Mods:\n\n"

    for m in mods:
        text += f"{m[0]} - {m[1]}\n"


    bot.send_message(
        call.message.chat.id,
        text
    )



# DELETE

@bot.callback_query_handler(
    func=lambda c:c.data=="delete"
)
def delete_start(call):

    if not is_admin(call.from_user.id):
        return


    bot.send_message(
        call.message.chat.id,
        "Send Mod ID:"
    )


    admin_state[
        call.from_user.id
    ] = "delete"



@bot.message_handler(
    func=lambda m:
    is_admin(m.from_user.id)
    and admin_state.get(m.from_user.id)=="delete"
)
def delete_mod(message):

    con = connect()
    cur = con.cursor()

    cur.execute(
        "DELETE FROM mods WHERE id=?",
        (message.text,)
    )

    con.commit()
    con.close()


    del admin_state[
        message.from_user.id
    ]


    bot.send_message(
        message.chat.id,
        "Deleted"
    )



print("ONYX STREET BOT RUNNING")

bot.infinity_polling()
