import telebot
from telebot import types
import sqlite3

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"

ADMIN_ID = 8356358583

CHANNEL = "@Onyx_Street"

BOT_USERNAME = "OnyxStreetbot"


bot = telebot.TeleBot(TOKEN)

DB = "mods.db"


# ---------- DATABASE ----------

def db():

    return sqlite3.connect(DB)



def setup():

    conn = db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS mods(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        type TEXT,
        file_id TEXT,
        url TEXT
    )
    """)

    conn.commit()
    conn.close()


setup()



# ---------- HELPERS ----------

def is_admin(user_id):

    return user_id == ADMIN_ID



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
            "I Joined",
            callback_data="check_join"
        )
    )

    return kb



# ---------- START ----------

@bot.message_handler(commands=["start"])
def start(message):

    args = message.text.split()


    if len(args) > 1:

        if not check_join(
            message.from_user.id
        ):

            bot.send_message(
                message.chat.id,
                "Please join the channel first.",
                reply_markup=join_keyboard()
            )

            return


        mod_id = args[1].replace(
            "mod_",
            ""
        )


        send_mod(
            message.chat.id,
            int(mod_id)
        )

        return



    kb = types.InlineKeyboardMarkup()


    kb.add(
        types.InlineKeyboardButton(
            "Mods",
            callback_data="mods"
        )
    )


    if is_admin(
        message.from_user.id
    ):

        kb.add(
            types.InlineKeyboardButton(
                "Admin Panel",
                callback_data="admin"
            )
        )


    bot.send_message(
        message.chat.id,
        "Welcome to ONYX STREET",
        reply_markup=kb
    )



@bot.callback_query_handler(
    func=lambda c:c.data=="check_join"
)
def check_join_button(call):

    if check_join(
        call.from_user.id
    ):

        bot.answer_callback_query(
            call.id,
            "Verified"
        )

        bot.send_message(
            call.message.chat.id,
            "You can open the mod link now."
        )

    else:

        bot.answer_callback_query(
            call.id,
            "You are not joined yet."
        )
admin_state = {}


# ---------- ADMIN PANEL ----------

@bot.message_handler(commands=["admin"])
def admin(message):

    if not is_admin(message.from_user.id):
        return


    admin_menu(
        message.chat.id
    )



def admin_menu(chat_id):

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "➕ Add Mod",
            callback_data="add_mod"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "🗑 Delete Mod",
            callback_data="delete_mod"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "📦 My Mods",
            callback_data="my_mods"
        )
    )


    bot.send_message(
        chat_id,
        "⚙️ Admin Panel",
        reply_markup=kb
    )



# ---------- ADD MOD ----------

@bot.callback_query_handler(
    func=lambda c:c.data=="add_mod"
)
def add_mod(call):

    if not is_admin(call.from_user.id):
        return


    admin_state[call.from_user.id] = {
        "step":"name"
    }


    bot.send_message(
        call.message.chat.id,
        "Send mod name:"
    )



@bot.message_handler(
    func=lambda m:
    is_admin(m.from_user.id)
    and m.from_user.id in admin_state
    and admin_state[m.from_user.id]["step"]=="name"
)
def mod_name(message):

    admin_state[
        message.from_user.id
    ]["name"] = message.text


    admin_state[
        message.from_user.id
    ]["step"]="type"



    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "📁 File",
            callback_data="add_file"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "🔗 Link",
            callback_data="add_link"
        )
    )


    bot.send_message(
        message.chat.id,
        "Choose type:",
        reply_markup=kb
    )



@bot.callback_query_handler(
    func=lambda c:c.data in [
        "add_file",
        "add_link"
    ]
)
def mod_type(call):

    if not is_admin(call.from_user.id):
        return


    if call.data=="add_file":

        admin_state[
            call.from_user.id
        ]["step"]="file"


        bot.send_message(
            call.message.chat.id,
            "Send file:"
        )


    else:

        admin_state[
            call.from_user.id
        ]["step"]="link"


        bot.send_message(
            call.message.chat.id,
            "Send download link:"
        )



# ---------- SAVE FILE ----------

@bot.message_handler(
    content_types=["document"]
)
def save_file(message):

    if not is_admin(message.from_user.id):
        return


    if message.from_user.id not
