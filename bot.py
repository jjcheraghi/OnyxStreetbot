import telebot
from telebot import types
import json
import os

# =========================
# SETTINGS
# =========================

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"

ADMIN_ID = 8356358583
CHANNEL = "@Onyx_Street"

bot = telebot.TeleBot(TOKEN)

DB_FILE = "mods.json"


# =========================
# DATABASE
# =========================

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False)


def load_mods():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_mods(mods):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(mods, f, indent=4, ensure_ascii=False)


# =========================
# ADMIN STATES
# =========================

admin_state = {}


# =========================
# CHECK ADMIN
# =========================

def is_admin(user_id):
    return user_id == ADMIN_ID


# =========================
# CHECK CHANNEL MEMBERSHIP
# =========================

def is_member(user_id):

    try:
        member = bot.get_chat_member(CHANNEL, user_id)

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:
        return False


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    if not is_member(message.from_user.id):

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "📢 عضویت در کانال",
                url="https://t.me/Onyx_Street"
            )
        )

        bot.send_message(
            message.chat.id,
            "❌ برای استفاده از ربات ابتدا عضو کانال شوید.",
            reply_markup=keyboard
        )

        return

    keyboard = types.InlineKeyboardMarkup()

    if is_admin(message.from_user.id):

        keyboard.add(
            types.InlineKeyboardButton(
                "⚙️ پنل ادمین",
                callback_data="admin_panel"
            )
        )

    bot.send_message(
        message.chat.id,
        "🚗 به ربات مود Onyx Street خوش آمدید.",
        reply_markup=keyboard
    )


# =========================
# ADMIN COMMAND
# =========================

@bot.message_handler(commands=["admin"])
def admin_command(message):

    if not is_admin(message.from_user.id):

        bot.reply_to(
            message,
            "❌ شما دسترسی ادمین ندارید."
        )

        return

    show_admin_panel(message.chat.id)


# =========================
# ADMIN PANEL
# =========================

def show_admin_panel(chat_id):

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "➕ اضافه کردن مود",
            callback_data="add_mod"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🗑 حذف مود",
            callback_data="delete_mod"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📦 لیست مودها",
            callback_data="list_mods"
        )
    )

    bot.send_message(
        chat_id,
        "⚙️ پنل مدیریت\n\n"
        "عملیات موردنظر را انتخاب کنید:",
        reply_markup=keyboard
    )


# =========================
# ADMIN PANEL BUTTON
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "admin_panel"
)
def admin_panel_button(call):

    if not is_admin(call.from_user.id):
        return

    show_admin_panel(call.message.chat.id)

    bot.answer_callback_query(call.id)


# =========================
# ADD MOD
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "add_mod"
)
def add_mod(call):

    if not is_admin(call.from_user.id):
        return

    admin_state[call.from_user.id] = {
        "step": "name"
    }

    bot.send_message(
        call.message.chat.id,
        "📝 نام مود را ارسال کن:"
    )

    bot.answer_callback_query(call.id)


# =========================
# ADMIN TEXT INPUT
# =========================

@bot.message_handler(
    func=lambda message:
    is_admin(message.from_user.id)
    and message.from_user.id in admin_state
)
def admin_text(message):

    state = admin_state[message.from_user.id]

    # NAME
    if state["step"] == "name":

        state["name"] = message.text
        state["step"] = "type"

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "📤 فایل",
                callback_data="type_file"
            )
        )

        keyboard.add(
            types.InlineKeyboardButton(
                "🔗 لینک",
                callback_data="type_link"
            )
        )

        bot.send_message(
            message.chat.id,
            "نوع مود را انتخاب کن:",
            reply_markup=keyboard
        )


# =========================
# FILE TYPE
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "type_file"
)
def type_file(call):

    if not is_admin(call.from_user.id):
        return

    if call.from_user.id not in admin_state:
        return

    admin_state[call.from_user.id]["step"] = "file"

    bot.send_message(
        call.message.chat.id,
        "📤 حالا فایل مود را ارسال کن:"
    )

    bot.answer_callback_query(call.id)


# =========================
# LINK TYPE
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "type_link"
)
def type_link(call):

    if not is_admin(call.from_user.id):
        return

    if call.from_user.id not in admin_state:
        return

    admin_state[call.from_user.id]["step"] = "link"

    bot.send_message(
        call.message.chat.id,
        "🔗 حالا لینک دانلود مود را ارسال کن:"
    )

    bot.answer_callback_query(call.id)


# =========================
# RECEIVE FILE
# =========================

@bot.message_handler(
    content_types=["document"]
)
def receive_file(message):

    if not is_admin(message.from_user.id):
        return

    if message.from_user.id not in admin_state:
        return

    state = admin_state[message.from_user.id]

    if state["step"] != "file":
        return

    mods = load_mods()

    new_id = len(mods) + 1

    mods.append({
        "id": new_id,
        "name": state["name"],
        "type": "file",
        "file_id": message.document.file_id
    })

    save_mods(mods)

    del admin_state[message.from_user.id]

    bot.send_message(
        message.chat.id,
        f"✅ مود با موفقیت اضافه شد.\n\n"
        f"📦 {state['name']}\n"
        f"🆔 ID: {new_id}"
    )


# =========================
# RECEIVE LINK
# =========================

@bot.message_handler(
    func=lambda message:
    is_admin(message.from_user.id)
    and message.from_user.id in admin_state
    and admin_state[message.from_user.id]["step"] == "link"
)
def receive_link(message):

    state = admin_state[message.from_user.id]

    mods = load_mods()

    new_id = len(mods) + 1

    mods.append({
        "id": new_id,
        "name": state["name"],
        "type": "link",
        "link": message.text
    })

    save_mods(mods)

    del admin_state[message.from_user.id]

    bot.send_message(
        message.chat.id,
        f"✅ مود با موفقیت اضافه شد.\n\n"
        f"📦 {state['name']}\n"
        f"🆔 ID: {new_id}"
    )


# =========================
# LIST MODS
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "list_mods"
)
def list_mods(call):

    if not is_admin(call.from_user.id):
        return

    mods = load_mods()

    if not mods:

        bot.send_message(
            call.message.chat.id,
            "📦 هنوز هیچ مودی اضافه نشده."
        )

        return

    text = "📦 لیست مودها:\n\n"

    for mod in mods:

        text += (
            f"🆔 {mod['id']}\n"
            f"📦 {mod['name']}\n"
            f"📌 نوع: {mod['type']}\n\n"
        )

    bot.send_message(
        call.message.chat.id,
        text
    )

    bot.answer_callback_query(call.id)


# =========================
# DELETE MOD MENU
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "delete_mod"
)
def delete_mod_menu(call):

    if not is_admin(call.from_user.id):
        return

    mods = load_mods()

    if not mods:

        bot.send_message(
            call.message.chat.id,
            "❌ هیچ مودی برای حذف وجود ندارد."
        )

        return

    keyboard = types.InlineKeyboardMarkup()

    for mod in mods:

        keyboard.add(
            types.InlineKeyboardButton(
                f"🗑 {mod['id']} - {mod['name']}",
                callback_data=f"delete_{mod['id']}"
            )
        )

    bot.send_message(
        call.message.chat.id,
        "🗑 مود موردنظر برای حذف را انتخاب کن:",
        reply_markup=keyboard
    )

    bot.answer_callback_query(call.id)


# =========================
# DELETE MOD
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("delete_")
)
def delete_mod(call):

    if not is_admin(call.from_user.id):
        return

    mod_id = int(
        call.data.split("_")[1]
    )

    mods = load_mods()

    new_mods = [
        mod for mod in mods
        if mod["id"] != mod_id
    ]

    if len(new_mods) == len(mods):

        bot.answer_callback_query(
            call.id,
            "❌ مود پیدا نشد.",
            show_alert=True
        )

        return

    # مرتب کردن IDها
    for index, mod in enumerate(new_mods, start=1):
        mod["id"] = index

    save_mods(new_mods)

    bot.answer_callback_query(
        call.id,
        "✅ مود حذف شد.",
        show_alert=True
    )

    bot.send_message(
        call.message.chat.id,
        "✅ مود با موفقیت حذف شد."
    )


# =========================
# RUN BOT
# =========================

print("ONYX STREET BOT STARTED")

bot.infinity_polling(
    skip_pending=True
        )
