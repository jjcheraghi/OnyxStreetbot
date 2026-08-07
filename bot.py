import telebot
from telebot import types
import json
import os
import time

# =========================================================
# SETTINGS
# =========================================================

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"

ADMIN_ID = 8356358583
CHANNEL = "@Onyx_Street"
CHANNEL_URL = "https://t.me/Onyx_Street"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

DB_FILE = "database.json"


# =========================================================
# DATABASE
# =========================================================

DEFAULT_DB = {
    "users": [],
    "mods": [],
    "categories": [
        "GTA SA",
        "GTA V",
        "NFS MW 2012",
        "BeamNG",
        "Assetto Corsa",
        "ETS2",
        "ATS",
        "Other"
    ]
}


def load_db():

    if not os.path.exists(DB_FILE):

        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(
                DEFAULT_DB,
                f,
                indent=4,
                ensure_ascii=False
            )

        return DEFAULT_DB.copy()

    try:

        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)

        # جلوگیری از خراب شدن دیتابیس قدیمی
        for key in DEFAULT_DB:

            if key not in db:
                db[key] = DEFAULT_DB[key]

        return db

    except Exception:

        return DEFAULT_DB.copy()


def save_db(db):

    with open(DB_FILE, "w", encoding="utf-8") as f:

        json.dump(
            db,
            f,
            indent=4,
            ensure_ascii=False
        )


# =========================================================
# ADMIN STATE
# =========================================================

admin_state = {}


# =========================================================
# BASIC FUNCTIONS
# =========================================================

def is_admin(user_id):

    return user_id == ADMIN_ID


def is_member(user_id):

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

    except Exception:

        return False


def register_user(user):

    db = load_db()

    user_id = user.id

    exists = any(
        u["id"] == user_id
        for u in db["users"]
    )

    if not exists:

        db["users"].append({
            "id": user_id,
            "username": user.username or "",
            "first_name": user.first_name or "",
            "joined_at": int(time.time())
        })

        save_db(db)


def next_mod_id(db):

    if not db["mods"]:
        return 1

    return max(
        mod["id"]
        for mod in db["mods"]
    ) + 1


def mod_code(mod_id):

    return f"ONYX{mod_id:03d}"


def find_mod(mod_id):

    db = load_db()

    for mod in db["mods"]:

        if mod["id"] == mod_id:
            return mod

    return None


# =========================================================
# JOIN MESSAGE
# =========================================================

def send_join_message(chat_id):

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "📢 عضویت در کانال",
            url=CHANNEL_URL
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "✅ بررسی عضویت",
            callback_data="check_join"
        )
    )

    bot.send_message(
        chat_id,
        "🔒 برای استفاده از ربات ابتدا در کانال Onyx Street عضو شوید.",
        reply_markup=keyboard
    )


# =========================================================
# MAIN MENU
# =========================================================

def main_menu(user_id):

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        types.InlineKeyboardButton(
            "📦 مودها",
            callback_data="mods"
        ),
        types.InlineKeyboardButton(
            "🔎 جستجو",
            callback_data="search"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🆕 آخرین مودها",
            callback_data="latest"
        ),
        types.InlineKeyboardButton(
            "📂 دسته‌بندی",
            callback_data="categories"
        )
    )

    if is_admin(user_id):

        keyboard.add(
            types.InlineKeyboardButton(
                "⚙️ پنل ادمین",
                callback_data="admin"
            )
        )

    return keyboard


# =========================================================
# /START
# =========================================================

@bot.message_handler(commands=["start"])
def start(message):

    register_user(message.from_user)

    if not is_member(message.from_user.id):

        send_join_message(message.chat.id)
        return

    bot.send_message(
        message.chat.id,
        "🚗 <b>ONYX STREET</b>\n\n"
        "مرکز دانلود مودهای خودرو\n\n"
        "یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=main_menu(
            message.from_user.id
        )
    )


# =========================================================
# /ADMIN
# =========================================================

@bot.message_handler(commands=["admin"])
def admin_command(message):

    if not is_admin(message.from_user.id):

        bot.reply_to(
            message,
            "❌ دسترسی غیرمجاز."
        )

        return

    show_admin_panel(
        message.chat.id
    )


# =========================================================
# ADMIN PANEL
# =========================================================

def show_admin_panel(chat_id):

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        types.InlineKeyboardButton(
            "➕ افزودن مود",
            callback_data="admin_add"
        ),
        types.InlineKeyboardButton(
            "🗑 حذف مود",
            callback_data="admin_delete"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "✏️ ویرایش مود",
            callback_data="admin_edit"
        ),
        types.InlineKeyboardButton(
            "📦 لیست مودها",
            callback_data="admin_list"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📊 آمار",
            callback_data="admin_stats"
        ),
        types.InlineKeyboardButton(
            "📢 پیام همگانی",
            callback_data="admin_broadcast"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📂 دسته‌بندی‌ها",
            callback_data="admin_categories"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🏠 منوی اصلی",
            callback_data="home"
        )
    )

    bot.send_message(
        chat_id,
        "⚙️ <b>پنل مدیریت ONYX STREET</b>\n\n"
        "عملیات موردنظر را انتخاب کنید:",
        reply_markup=keyboard
    )


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


# =========================================================
# HOME
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "home"
)
def home(call):

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        "🏠 منوی اصلی:",
        reply_markup=main_menu(
            call.from_user.id
        )
    )


# =========================================================
# JOIN CHECK
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "check_join"
)
def check_join(call):

    if is_member(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "✅ عضویت شما تأیید شد."
        )

        bot.send_message(
            call.message.chat.id,
            "🚗 خوش آمدید به ONYX STREET",
            reply_markup=main_menu(
                call.from_user.id
            )
        )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ هنوز عضو کانال نیستید.",
            show_alert=True
        )


# =========================================================
# ADD MOD - START
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "admin_add"
)
def admin_add(call):

    if not is_admin(call.from_user.id):
        return

    bot.answer_callback_query(call.id)

    admin_state[call.from_user.id] = {
        "step": "name"
    }

    bot.send_message(
        call.message.chat.id,
        "➕ <b>افزودن مود</b>\n\n"
        "📝 نام مود را ارسال کنید:"
    )


# =========================================================
# ADMIN TEXT STATE HANDLER
# =========================================================

@bot.message_handler(
    func=lambda message:
        is_admin(message.from_user.id)
        and message.from_user.id in admin_state
        and admin_state[
            message.from_user.id
        ].get("step") in [
            "name",
            "category",
            "description",
            "size",
            "version",
            "link"
        ]
)
def admin_state_text(message):

    state = admin_state[
        message.from_user.id
    ]

    step = state["step"]

    # -------------------------
    # NAME
    # -------------------------

    if step == "name":

        state["name"] = message.text.strip()
        state["step"] = "category"

        db = load_db()

        keyboard = types.InlineKeyboardMarkup(
            row_width=2
        )

        for category in db["categories"]:

            keyboard.add(
                types.InlineKeyboardButton(
                    category,
                    callback_data=
                    "cat_" + category
                )
            )

        bot.send_message(
            message.chat.id,
            "📂 دسته‌بندی مود را انتخاب کنید:",
            reply_markup=keyboard
        )

    # -------------------------
    # DESCRIPTION
    # -------------------------

    elif step == "description":

        state["description"] = message.text.strip()
        state["step"] = "size"

        bot.send_message(
            message.chat.id,
            "📦 حجم مود را وارد کنید.\n\n"
            "مثال:\n"
            "<code>1.2 GB</code>\n\n"
            "اگر مشخص نیست بنویسید:\n"
            "<code>Unknown</code>"
        )

    # -------------------------
    # SIZE
    # -------------------------

    elif step == "size":

        state["size"] = message.text.strip()
        state["step"] = "version"

        bot.send_message(
            message.chat.id,
            "🔖 نسخه مود را وارد کنید.\n\n"
            "مثال:\n"
            "<code>V1.0</code>"
        )

    # -------------------------
    # VERSION
    # -------------------------

    elif step == "version":

        state["version"] = message.text.strip()

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "📤 فایل",
                callback_data="add_type_file"
            ),
            types.InlineKeyboardButton(
                "🔗 لینک",
                callback_data="add_type_link"
            )
        )

        state["step"] = "type"

        bot.send_message(
            message.chat.id,
            "نوع دانلود را انتخاب کنید:",
            reply_markup=keyboard
        )

    # -------------------------
    # LINK
    # -------------------------

    elif step == "link":

        link = message.text.strip()

        if not (
            link.startswith("http://")
            or link.startswith("https://")
        ):

            bot.send_message(
                message.chat.id,
                "❌ لینک معتبر نیست.\n"
                "لینک باید با http:// یا https:// شروع شود."
            )

            return

        state["link"] = link

        save_new_mod(
            message.chat.id,
            message.from_user.id
        )


# =========================================================
# CATEGORY SELECT
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("cat_")
)
def select_category(call):

    if not is_admin(call.from_user.id):
        return

    if call.from_user.id not in admin_state:
        return

    category = call.data[4:]

    state = admin_state[
        call.from_user.id
    ]

    state["category"] = category
    state["step"] = "description"

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        "📝 توضیحات مود را ارسال کنید:"
    )


# =========================================================
# TYPE FILE
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "add_type_file"
)
def add_type_file(call):

    if not is_admin(call.from_user.id):
        return

    if call.from_user.id not in admin_state:
        return

    state = admin_state[
        call.from_user.id
    ]

    state["step"] = "file"

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        "📤 حالا فایل مود را ارسال کنید."
    )


# =========================================================
# TYPE LINK
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "add_type_link"
)
def add_type_link(call):

    if not is_admin(call.from_user.id):
        return

    if call.from_user.id not in admin_state:
        return

    state = admin_state[
        call.from_user.id
    ]

    state["step"] = "link"

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        "🔗 لینک دانلود را ارسال کنید:"
    )


# =========================================================
# RECEIVE FILE
# =========================================================

@bot.message_handler(
    content_types=[
        "document",
        "video",
        "audio"
    ]
)
def receive_file(message):

    if not is_admin(message.from_user.id):
        return

    if message.from_user.id not in admin_state:
        return

    state = admin_state[
        message.from_user.id
    ]

    if state.get("step") != "file":
        return

    if message.content_type == "document":

        file_id = message.document.file_id

    elif message.content_type == "video":

        file_id = message.video.file_id

    else:

        file_id = message.audio.file_id

    state["file_id"] = file_id
    state["type"] = "file"

    save_new_mod(
        message.chat.id,
        message.from_user.id
    )


# =========================================================
# SAVE NEW MOD
# =========================================================

def save_new_mod(chat_id, user_id):

    if user_id not in admin_state:
        return

    state = admin_state[user_id]

    db = load_db()

    new_id = next_mod_id(db)

    mod = {
        "id": new_id,
        "code": mod_code(new_id),
        "name": state["name"],
        "category": state["category"],
        "description": state["description"],
        "size": state["size"],
        "version": state["version"],
        "type": state.get("type", "link"),
        "file_id": state.get("file_id", ""),
        "link": state.get("link", ""),
        "downloads": 0,
        "rating_total": 0,
        "rating_count": 0,
        "created_at": int(time.time())
    }

    db["mods"].append(mod)

    save_db(db)

    del admin_state[user_id]

    bot.send_message(
        chat_id,
        "✅ <b>مود با موفقیت اضافه شد!</b>\n\n"
        f"🚗 {mod['name']}\n"
        f"📂 {mod['category']}\n"
        f"🆔 #{mod['code']}"
    )


# =========================================================
# USER MODS MENU
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "mods"
)
def user_mods(call):

    if not is_member(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "ابتدا عضو کانال شوید.",
            show_alert=True
        )

        return

    bot.answer_callback_query(call.id)

    show_mod_page(
        call.message.chat.id,
        0
    )


# =========================================================
# SHOW MOD PAGE
# =========================================================

def show_mod_page(chat_id, page):

    db = load_db()

    mods = db["mods"]

    if not mods:

        bot.send_message(
            chat_id,
            "📦 هنوز هیچ مودی اضافه نشده."
        )

        return

    per_page = 8

    start_index = page * per_page
    end_index = start_index + per_page

    current = mods[
        start_index:end_index
    ]

    keyboard = types.InlineKeyboardMarkup(
        row_width=1
    )

    for mod in current:

        keyboard.add(
            types.InlineKeyboardButton(
                f"🚗 {mod['name']}",
                callback_data=
                f"view_{mod['id']}"
            )
        )

    navigation = []

    if page > 0:

        navigation.append(
            types.InlineKeyboardButton(
                "⬅️ قبلی",
                callback_data=
                f"mods_page_{page-1}"
            )
        )

    if end_index < len(mods):

        navigation.append(
            types.InlineKeyboardButton(
                "بعدی ➡️",
                callback_data=
                f"mods_page_{page+1}"
            )
        )

    if navigation:
        keyboard.row(*navigation)

    keyboard.add(
        types.InlineKeyboardButton(
            "🏠 منوی اصلی",
            callback_data="home"
        )
    )

    bot.send_message(
        chat_id,
        "📦 <b>مودها</b>\n\n"
        "مود موردنظر را انتخاب کنید:",
        reply_markup=keyboard
    )


# =========================================================
# MOD PAGE
# =========================================================

@bot.callback_query_handler(
    func=lambda call:
        call.data.startswith("mods_page_")
)
def mods_page(call):

    page = int(
        call.data.split("_")[2]
    )

    bot.answer_callback_query(call.id)

    show_mod_page(
        call.message.chat.id,
        page
    )


# =========================================================
# VIEW MOD
# =========================================================

@bot.callback_query_handler(
    func=lambda call:
        call.data.startswith("view_")
)
def view_mod(call):

    mod_id = int(
        call.data.split("_")[1]
    )

    mod = find_mod(mod_id)

    if not mod:
        bot.answer_callback_query(
            call.id,
            "مود پیدا نشد.",
            show_alert=True
        )

        return

    if not is_member(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "ابتدا عضو کانال شوید.",
            show_alert=True
        )

        return

    rating = "بدون امتیاز"

    if mod["rating_count"] > 0:

        rating = round(
            mod["rating_total"] /
            mod["rating_count"],
            1
        )

        rating = f"{rating}/5"

    text = (
        f"🚗 <b>{mod['name']}</b>\n\n"
        f"🆔 #{mod['code']}\n"
        f"📂 دسته: {mod['category']}\n"
        f"📦 حجم: {mod['size']}\n"
        f"🔖 نسخه: {mod['version']}\n"
        f"⭐ امتیاز: {rating}\n"
        f"📥 دانلود: {mod['downloads']}\n\n"
        f"📝 <b>توضیحات:</b>\n"
        f"{mod['description']}"
    )

    keyboard = types.InlineKeyboardMarkup()

    if mod["type"] == "file":

        keyboard.add(
            types.InlineKeyboardButton(
                "📥 دریافت فایل",
                callback_data=
                f"download_{mod['id']}"
            )
        )

    else:

        keyboard.add(
            types.InlineKeyboardButton(
  
