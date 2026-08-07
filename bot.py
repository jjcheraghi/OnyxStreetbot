import telebot
from telebot import types
import json
import os

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"
ADMIN_ID = 8356358583

CHANNEL = "@Onyx_Street"
BOT_USERNAME = "YOUR_BOT_USERNAME"

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
