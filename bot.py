import telebot
from telebot import types
import json
import os

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"
ADMIN_ID = 8356358583

CHANNEL = "@Onyx_Street"
BOT_USERNAME = "@OnyxStreetbot"

bot = telebot.TeleBot(TOKEN)

DB = "mods.json"

admin_mode = {}


def load_mods():
    if not os.path.exists(DB):
        return []

    with open(DB, "r", encoding="utf-8") as f:
        return json.load(f)


def save_mods(data):
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


def is_admin(uid):
    return uid == ADMIN_ID


def check_member(user_id):

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


def force_join():

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "Join Channel",
            url=f"https://t.me/{CHANNEL.replace('@','')}"
        )
    )

    return kb


@bot.message_handler(commands=["start"])
def start(message):

    args = message.text.split()

    if len(args) > 1:

        if not check_member(message.from_user.id):

            bot.send_message(
                message.chat.id,
                "Please join the channel first.",
                reply_markup=force_join()
            )

            return


        mod_id = int(
            args[1].replace("mod_", "")
        )

        send_mod(
            message.chat.id,
            mod_id
        )

        return


    bot.send_message(
        message.chat.id,
        "Welcome to ONYX STREET"
    )


@bot.message_handler(commands=["admin"])
def admin(message):

    if not is_admin(message.from_user.id):
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
            "Mod List",
            callback_data="list"
        )
    )

    bot.send_message(
        message.chat.id,
        "Admin Panel",
        reply_markup=kb
    )
@bot.callback_query_handler(
    func=lambda c: c.data == "add"
)
def add_mod(c):

    if not is_admin(c.from_user.id):
        return

    admin_mode[c.from_user.id] = {
        "step": "name"
    }

    bot.send_message(
        c.message.chat.id,
        "Send mod name:"
    )


@bot.message_handler(
    func=lambda m:
    is_admin(m.from_user.id)
    and m.from_user.id in admin_mode
    and admin_mode[m.from_user.id]["step"] == "name"
)
def get_name(m):

    admin_mode[m.from_user.id]["name"] = m.text

    admin_mode[m.from_user.id]["step"] = "type"

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "File",
            callback_data="file"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "Link",
            callback_data="link"
        )
    )

    bot.send_message(
        m.chat.id,
        "Select type:",
        reply_markup=kb
    )


@bot.callback_query_handler(
    func=lambda c:
    c.data in ["file","link"]
)
def select_type(c):

    if not is_admin(c.from_user.id):
        return

    admin_mode[c.from_user.id]["step"] = c.data

    if c.data == "file":

        bot.send_message(
            c.message.chat.id,
            "Send file:"
        )

    else:

        bot.send_message(
            c.message.chat.id,
            "Send download link:"
        )



@bot.message_handler(
    content_types=["document"]
)
def receive_file(m):

    if not is_admin(m.from_user.id):
        return

    if m.from_user.id not in admin_mode:
        return


    data = admin_mode[m.from_user.id]


    if data["step"] != "file":
        return


    mods = load_mods()

    mod_id = len(mods) + 1


    mods.append({

        "id": mod_id,
        "name": data["name"],
        "type": "file",
        "file_id": m.document.file_id

    })


    save_mods(mods)

    del admin_mode[m.from_user.id]


    link = (
        f"https://t.me/{BOT_USERNAME}"
        f"?start=mod_{mod_id}"
    )


    bot.send_message(
        m.chat.id,
        "Mod added.\n\n"
        f"Mod Link:\n{link}"
    )



@bot.message_handler(
    func=lambda m:
    is_admin(m.from_user.id)
    and m.from_user.id in admin_mode
    and admin_mode[m.from_user.id]["step"] == "link"
)
def receive_link(m):

    data = admin_mode[m.from_user.id]

    mods = load_mods()

    mod_id = len(mods) + 1


    mods.append({

        "id": mod_id,
        "name": data["name"],
        "type": "link",
        "url": m.text

    })


    save_mods(mods)

    del admin_mode[m.from_user.id]


    link = (
        f"https://t.me/{BOT_USERNAME}"
        f"?start=mod_{mod_id}"
    )


    bot.send_message(
        m.chat.id,
        "Mod added.\n\n"
        f"Mod Link:\n{link}"
    )
