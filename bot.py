import telebot
from telebot import types
import json
import os

# =========================
# SETTINGS
# =========================

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"
ADMIN_ID = 8356358583

bot = telebot.TeleBot(TOKEN)

DB_FILE = "mods.json"


# =========================
# DATABASE
# =========================

def load_mods():
    if not os.path.exists(DB_FILE):
        return []

    try:
        with open(DB_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return []


def save_mods(mods):
    with open(DB_FILE, "w", encoding="utf-8") as file:
        json.dump(
            mods,
            file,
            ensure_ascii=False,
            indent=4
        )


# =========================
# ADMIN CHECK
# =========================

def is_admin(user_id):
    return user_id == ADMIN_ID


# =========================
# TEMPORARY ADMIN DATA
# =========================

admin_data = {}


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "📦 لیست مودها",
            callback_data="mods"
        )
    )

    if is_admin(message.from_user.id):

        keyboard.add(
            types.InlineKeyboardButton(
                "⚙️ پنل ادمین",
                callback_data="admin"
            )
        )

    bot.send_message(
        message.chat.id,
        "🚗 <b>ONYX STREET</b>\n\n"
        "به ربات دانلود مود خوش آمدید.",
        reply_markup=keyboard
    )


# =========================
# ADMIN COMMAND
# =========================

@bot.message_handler(commands=["admin"])
def admin_command(message):

    if not is_admin(message.from_user.id):

        bot.send_message(
            message.chat.id,
            "❌ دسترسی ندارید."
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
            callback_data="add"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🗑 حذف مود",
            callback_data="delete"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📦 لیست مودها",
            callback_data="mods"
        )
    )

    bot.send_message(
        chat_id,
        "⚙️ <b>پنل ادمین</b>\n\n"
        "یک گزینه را انتخاب کنید:",
        reply_markup=keyboard
    )


# =========================
# ADMIN BUTTON
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "admin"
)
def admin_button(call):

    if not is_admin(call.from_user.id):
        return

    bot.answer_callback_query(call.id)

    show_admin_panel(
        call.message.chat.id
    )


# =========================
# ADD MOD
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "add"
)
def add_mod(call):

    if not is_admin(call.from_user.id):
        return

    bot.answer_callback_query(call.id)

    admin_data[call.from_user.id] = {
        "step": "name"
    }

    bot.send_message(
        call.message.chat.id,
        "📝 نام مود را بفرست:"
    )


# =========================
# ADMIN TEXT
# =========================

@bot.message_handler(
    func=lambda message:
        is_admin(message.from_user.id)
        and message.from_user.id in admin_data
        and admin_data[
            message.from_user.id
        ]["step"] == "name"
)
def get_mod_name(message):

    admin_data[
        message.from_user.id
    ]["name"] = message.text

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "📤 فایل",
            callback_data="file"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🔗 لینک",
            callback_data="link"
        )
    )

    admin_data[
        message.from_user.id
    ]["step"] = "type"

    bot.send_message(
        message.chat.id,
        "نوع مود را انتخاب کن:",
        reply_markup=keyboard
    )


# =========================
# FILE TYPE
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "file"
)
def choose_file(call):

    if not is_admin(call.from_user.id):
        return

    if call.from_user.id not in admin_data:
        return

    admin_data[
        call.from_user.id
    ]["step"] = "file"

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        "📤 فایل مود را ارسال کن:"
    )


# =========================
# LINK TYPE
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "link"
)
def choose_link(call):

    if not is_admin(call.from_user.id):
        return

    if call.from_user.id not in admin_data:
        return

    admin_data[
        call.from_user.id
    ]["step"] = "link"

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        "🔗 لینک دانلود را ارسال کن:"
    )


# =========================
# RECEIVE FILE
# =========================

@bot.message_handler(
    content_types=["document"]
)
def receive_file(message):

    if not is_admin(message.from_user.id):
        return

    if message.from_user.id not in admin_data:
        return

    data = admin_data[
        message.from_user.id
    ]

    if data["step"] != "file":
        return

    mods = load_mods()

    new_id = 1

    if mods:
        new_id = max(
            mod["id"]
            for mod in mods
        ) + 1

    mods.append({
        "id": new_id,
        "name": data["name"],
        "type": "file",
        "file_id": message.document.file_id
    })

    save_mods(mods)

    del admin_data[
        message.from_user.id
    ]

    bot.send_message(
        message.chat.id,
        "✅ مود با موفقیت اضافه شد!\n\n"
        f"📦 {data['name']}\n"
        f"🆔 {new_id}"
    )


# =========================
# RECEIVE LINK
# =========================

@bot.message_handler(
    func=lambda message:
        is_admin(message.from_user.id)
        and message.from_user.id in admin_data
        and admin_data[
            message.from_user.id
        ]["step"] == "link"
)
def receive_link(message):

    data = admin_data[
        message.from_user.id
    ]

    mods = load_mods()

    new_id = 1

    if mods:
        new_id = max(
            mod["id"]
            for mod in mods
        ) + 1

    mods.append({
        "id": new_id,
        "name": data["name"],
        "type": "link",
        "link": message.text
    })

    save_mods(mods)

    del admin_data[
        message.from_user.id
    ]

    bot.send_message(
        message.chat.id,
        "✅ مود با موفقیت اضافه شد!\n\n"
        f"📦 {data['name']}\n"
        f"🆔 {new_id}"
    )


# =========================
# MOD LIST
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "mods"
)
def mods_list(call):

    mods = load_mods()

    bot.answer_callback_query(call.id)

    if not mods:

        bot.send_message(
            call.message.chat.id,
            "📦 هنوز هیچ مودی ثبت نشده."
        )

        return

    keyboard = types.InlineKeyboardMarkup()

    for mod in mods:

        keyboard.add(
            types.InlineKeyboardButton(
                f"📦 {mod['name']}",
                callback_data=
                f"mod_{mod['id']}"
            )
        )

    bot.send_message(
        call.message.chat.id,
        "📦 <b>لیست مودها</b>",
        reply_markup=keyboard
    )


# =========================
# SHOW MOD
# =========================

@bot.callback_query_handler(
    func=lambda call:
        call.data.startswith("mod_")
)
def show_mod(call):

    mod_id = int(
        call.data.split("_")[1]
    )

    mods = load_mods()

    mod = None

    for item in mods:

        if item["id"] == mod_id:
            mod = item
            break

    if mod is None:

        bot.answer_callback_query(
            call.id,
            "مود پیدا نشد.",
            show_alert=True
        )

        return

    keyboard = types.InlineKeyboardMarkup()

    if mod["type"] == "file":

        keyboard.add(
            types.InlineKeyboardButton(
                "📥 دریافت فایل",
                callback_data=
                f"download_{mod_id}"
            )
        )

    else:

        keyboard.add(
            types.InlineKeyboardButton(
                "🔗 دانلود",
                url=mod["link"]
            )
        )

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        f"🚗 <b>{mod['name']}</b>\n\n"
        f"🆔 {mod['id']}",
        reply_markup=keyboard
    )


# =========================
# DOWNLOAD FILE
# =========================

@bot.callback_query_handler(
    func=lambda call:
        call.data.startswith("download_")
)
def download_file(call):

    mod_id = int(
        call.data.split("_")[1]
    )

    mods = load_mods()

    for mod in mods:

        if mod["id"] == mod_id:

            if mod["type"] == "file":

                bot.send_document(
                    call.message.chat.id,
                    mod["file_id"]
                )

            break

    bot.answer_callback_query(call.id)


# =========================
# DELETE MENU
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "delete"
)
def delete_menu(call):

    if not is_admin(call.from_user.id):
        return

    mods = load_mods()

    bot.answer_callback_query(call.id)

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
                f"🗑 {mod['name']}",
                callback_data=
                f"del_{mod['id']}"
            )
        )

    bot.send_message(
        call.message.chat.id,
        "🗑 مود موردنظر را انتخاب کن:",
        reply_markup=keyboard
    )


# =========================
# DELETE MOD
# =========================

@bot.callback_query_handler(
    func=lambda call:
        call.data.startswith("del_")
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
            "مود پیدا نشد.",
            show_alert=True
        )

        return

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
# RUN
# =========================

print("ONYX STREET BOT STARTED")

bot.infinity_polling(
    skip_pending=True
    )
