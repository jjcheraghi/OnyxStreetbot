import telebot
import json
import os

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"

CHANNEL = "@Onyx_Street"
ADMIN_ID = 8356358583

bot = telebot.TeleBot(TOKEN)

DB = "mods.json"

if not os.path.exists(DB):
    with open(DB, "w") as f:
        json.dump([], f)


def load_mods():
    with open(DB, "r") as f:
        return json.load(f)


def save_mods(data):
    with open(DB, "w") as f:
        json.dump(data, f, indent=4)


def is_member(user_id):
    try:
        status = bot.get_chat_member(CHANNEL, user_id).status
        return status in ["member", "administrator", "creator"]
    except:
        return False


@bot.message_handler(commands=["start"])
def start(message):
    if not is_member(message.from_user.id):
        bot.reply_to(
            message,
            f"برای استفاده اول عضو کانال شوید:\n{CHANNEL}"
        )
        return

    bot.reply_to(
        message,
        "سلام 👋\nربات دانلود مود آماده است.\n\n"
        "/mods - لیست مودها"
    )


@bot.message_handler(commands=["mods"])
def mods(message):
    if not is_member(message.from_user.id):
        return

    data = load_mods()

    if not data:
        bot.reply_to(message, "هیچ مودی ثبت نشده.")
        return

    text = "📦 لیست مودها:\n\n"

    for m in data:
        text += f"🔹 {m['id']} - {m['name']}\n{m['link']}\n\n"

    bot.reply_to(message, text)


@bot.message_handler(commands=["add"])
def add(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.reply_to(
        message,
        "فرمت ارسال:\n\n"
        "نام مود | لینک دانلود\n\n"
        "یا بعد از دستور فایل را ارسال کنید."
    )


@bot.message_handler(content_types=["document"])
def file_upload(message):

    if message.from_user.id != ADMIN_ID:
        return

    data = load_mods()

    new_id = len(data)+1

    file_id = message.document.file_id

    data.append({
        "id": new_id,
        "name": message.document.file_name,
        "link": file_id,
        "type": "file"
    })

    save_mods(data)

    bot.reply_to(
        message,
        "✅ فایل مود ذخیره شد."
    )


@bot.message_handler(commands=["delete"])
def delete(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:
        num = int(message.text.split()[1])

        data = load_mods()

        data = [
            x for x in data
            if x["id"] != num
        ]

        save_mods(data)

        bot.reply_to(
            message,
            "✅ مود حذف شد."
        )

    except:
        bot.reply_to(
            message,
            "استفاده:\n/delete شماره"
        )


@bot.message_handler(func=lambda m: "|" in m.text)
def add_link(message):

    if message.from_user.id != ADMIN_ID:
        return

    name, link = message.text.split("|",1)

    data = load_mods()

    data.append({
        "id": len(data)+1,
        "name": name.strip(),
        "link": link.strip(),
        "type": "link"
    })

    save_mods(data)

    bot.reply_to(
        message,
        "✅ لینک مود اضافه شد."
    )


print("Bot Started...")
# وضعیت انتظار ادمین
admin_state = {}


# دکمه افزودن مود
@bot.callback_query_handler(func=lambda call: call.data=="add")
def add_mod(call):

    if call.from_user.id != ADMIN_ID:
        return

    admin_state[call.from_user.id] = "name"

    bot.send_message(
        call.message.chat.id,
        "📝 نام مود را ارسال کنید:"
    )



# دریافت اطلاعات ادمین
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin_input(message):

    user_id = message.from_user.id

    if user_id not in admin_state:
        return


    step = admin_state[user_id]


    # گرفتن نام
    if step == "name":

        admin_state[user_id] = {
            "name": message.text
        }

        bot.send_message(
            message.chat.id,
            "📂 دسته بندی مود را ارسال کنید:\n\n"
            "مثال:\n"
            "GTA V\n"
            "BeamNG\n"
            "Assetto Corsa"
        )

        admin_state[user_id]["step"] = "category"



    # گرفتن دسته
    elif isinstance(step, dict) and step["step"] == "category":

        step["category"] = message.text
        step["step"] = "file"

        bot.send_message(
            message.chat.id,
            "📦 حالا فایل مود را ارسال کنید\n"
            "یا لینک دانلود را بفرستید."
        )



# دریافت فایل
@bot.message_handler(content_types=["document"])
def get_file(message):

    if message.from_user.id != ADMIN_ID:
        return

    if message.from_user.id not in admin_state:
        return


    info = admin_state[message.from_user.id]

    if not isinstance(info, dict):
        return


    data = load_db()


    data.append({
        "id": len(data)+1,
        "name": info["name"],
        "category": info["category"],
        "type": "file",
        "file_id": message.document.file_id
    })


    save_db(data)

    del admin_state[message.from_user.id]


    bot.reply_to(
        message,
        "✅ مود با فایل ذخیره شد."
    )



# دریافت لینک
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def get_link(message):

    if message.from_user.id not in admin_state:
        return

    info = admin_state[message.from_user.id]

    if not isinstance(info, dict):
        return

    if info.get("step") == "file":

        data = load_db()


        data.append({
            "id": len(data)+1,
            "name": info["name"],
            "category": info["category"],
            "type": "link",
            "link": message.text
        })


        save_db(data)

        del admin_state[message.from_user.id]


        bot.reply_to(
            message,
            "✅ لینک مود ذخیره شد."
    )
 # نمایش لیست مودها
@bot.callback_query_handler(func=lambda call: call.data=="mods")
def show_mods(call):

    data = load_db()

    if not data:
        bot.answer_callback_query(
            call.id,
            "هیچ مودی ثبت نشده",
            show_alert=True
        )
        return


    kb = types.InlineKeyboardMarkup()


    for mod in data:
        kb.add(
            types.InlineKeyboardButton(
                f"{mod['name']} | {mod['category']}",
                callback_data=f"mod_{mod['id']}"
            )
        )


    bot.edit_message_text(
        "📦 لیست مودها:",
        call.message.chat.id,
        call.message.id,
        reply_markup=kb
    )



# باز کردن مود
@bot.callback_query_handler(func=lambda call: call.data.startswith("mod_"))
def open_mod(call):

    mod_id = int(call.data.split("_")[1])

    data = load_db()

    mod = None

    for m in data:
        if m["id"] == mod_id:
            mod = m
            break


    if not mod:
        return


    kb = types.InlineKeyboardMarkup()

    if mod["type"] == "file":

        kb.add(
            types.InlineKeyboardButton(
                "📥 دریافت فایل",
                callback_data=f"file_{mod_id}"
            )
        )

    else:

        kb.add(
            types.InlineKeyboardButton(
                "🔗 دانلود",
                url=mod["link"]
            )
        )


    bot.send_message(
        call.message.chat.id,
        f"🚗 {mod['name']}\n\n"
        f"📂 دسته: {mod['category']}",
        reply_markup=kb
    )



# ارسال فایل
@bot.callback_query_handler(func=lambda call: call.data.startswith("file_"))
def send_file(call):

    mod_id = int(call.data.split("_")[1])

    data = load_db()

    for mod in data:

        if mod["id"] == mod_id:

            bot.send_document(
                call.message.chat.id,
                mod["file_id"]
            )

            break



# حذف مود
@bot.callback_query_handler(func=lambda call: call.data=="delete")
def delete_menu(call):

    if call.from_user.id != ADMIN_ID:
        return


    data = load_db()

    kb = types.InlineKeyboardMarkup()


    for mod in data:
        kb.add(
            types.InlineKeyboardButton(
                f"🗑 {mod['name']}",
                callback_data=f"del_{mod['id']}"
            )
        )


    bot.send_message(
        call.message.chat.id,
        "مودی که می‌خواهی حذف شود را انتخاب کن:",
        reply_markup=kb
    )



@bot.callback_query_handler(func=lambda call: call.data.startswith("del_"))
def delete_confirm(call):

    if call.from_user.id != ADMIN_ID:
        return


    mod_id = int(call.data.split("_")[1])

    data = load_db()


    data = [
        m for m in data
        if m["id"] != mod_id
    ]


    # شماره‌ها دوباره مرتب شوند
    for i, m in enumerate(data):
        m["id"] = i + 1


    save_db(data)


    bot.answer_callback_query(
        call.id,
        "✅ مود حذف شد",
        show_alert=True
    )       

bot.infinity_polling()
