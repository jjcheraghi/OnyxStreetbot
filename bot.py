import telebot
import sqlite3
from datetime import datetime

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"

ADMIN_ID = 8356358583

CHANNEL = "@Onyx_Street"
CHANNEL_LINK = "https://t.me/Onyx_Street"

BOT_USERNAME = "OnyxStreetBot"

bot = telebot.TeleBot(TOKEN)

db = sqlite3.connect("onyx.db", check_same_thread=False)
cursor = db.cursor()


# جدول مودها
cursor.execute("""
CREATE TABLE IF NOT EXISTS mods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    game TEXT,
    photo TEXT,
    description TEXT,
    file_id TEXT,
    downloads INTEGER DEFAULT 0,
    date TEXT
)
""")


# جدول کاربران
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY
)
""")


db.commit()


# ذخیره کاربر
def save_user(user_id):
    cursor.execute(
        "INSERT OR IGNORE INTO users(id) VALUES(?)",
        (user_id,)
    )
    db.commit()


# بررسی عضویت
def check_membership(user_id):
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



# جوین اجباری
def join_keyboard():

    @bot.message_handler(commands=["start"])
def start(message):

    save_user(message.from_user.id)

    if not check_membership(message.from_user.id):

        bot.send_message(
            message.chat.id,
            "⚠️ برای استفاده از ربات ابتدا عضو کانال شوید:",
            reply_markup=join_keyboard()
        )
        return


    markup = telebot.types.InlineKeyboardMarkup(row_width=2)

    latest = telebot.types.InlineKeyboardButton(
        "🔥 جدیدترین مودها",
        callback_data="latest"
    )

    games = telebot.types.InlineKeyboardButton(
        "🎮 دسته‌بندی بازی‌ها",
        callback_data="games"
    )

    search = telebot.types.InlineKeyboardButton(
        "🔎 جستجو",
        callback_data="search"
    )

    channel = telebot.types.InlineKeyboardButton(
        "📢 کانال ما",
        url=CHANNEL_LINK
    )

    markup.add(latest, games)
    markup.add(search, channel)


    bot.send_message(
        message.chat.id,
        """
🚗 Onyx Street

مرجع دانلود مود بازی‌ها

یک گزینه را انتخاب کنید 👇
""",
        reply_markup=markup
    )
""",
    reply_markup=main_menu()
)
print("Onyx Street Bot Started")

# =========================
# User Menu
# =========================

def main_menu():

    markup = telebot.types.InlineKeyboardMarkup(row_width=2)

    latest = telebot.types.InlineKeyboardButton(
        "🔥 جدیدترین مودها",
        callback_data="latest"
    )

    games = telebot.types.InlineKeyboardButton(
        "🎮 دسته‌بندی بازی‌ها",
        callback_data="games"
    )

    search = telebot.types.InlineKeyboardButton(
        "🔎 جستجوی مود",
        callback_data="search"
    )

    channel = telebot.types.InlineKeyboardButton(
        "📢 کانال ما",
        url=CHANNEL_LINK
    )

    markup.add(latest, games)
    markup.add(search, channel)

    return markup



# جایگزین بخش پیام start
# (قسمت پیام خوش آمدگویی را با این عوض می‌کنیم)

@bot.message_handler(commands=["menu"])
def menu(message):

    if not check_membership(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "⚠️ ابتدا عضو کانال شوید:",
            reply_markup=join_keyboard()
        )
        return


    bot.send_message(
        message.chat.id,
        """
🚗 Onyx Street

مرجع دانلود مود بازی‌ها

یک گزینه انتخاب کنید 👇
""",
        reply_markup=main_menu()
    )



# =========================
# Game Categories
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "games"
)
def games(call):

    markup = telebot.types.InlineKeyboardMarkup()

    game_list = [
        ("🏎 Assetto Corsa", "Assetto Corsa"),
        ("🚙 BeamNG Drive", "BeamNG Drive"),
        ("🚘 GTA V", "GTA V"),
        ("🏙 GTA San Andreas", "GTA SA"),
        ("🚛 ETS2", "ETS2"),
        ("🚚 ATS", "ATS"),
        ("🏁 NFS Most Wanted 2012", "NFS MW 2012")
    ]


    for title, data in game_list:

        markup.add(
            telebot.types.InlineKeyboardButton(
                title,
                callback_data=f"game_{data}"
            )
        )


    bot.edit_message_text(
        "🎮 بازی مورد نظر را انتخاب کنید:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )



# =========================
# Latest Mods
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "latest"
)
def latest(call):

    cursor.execute(
        """
        SELECT id,name,game
        FROM mods
        ORDER BY id DESC
        LIMIT 10
        """
    )

    mods = cursor.fetchall()


    if not mods:

        bot.send_message(
            call.message.chat.id,
            "❌ هنوز مود ثبت نشده"
        )

        return


    text = "🔥 جدیدترین مودها:\n\n"

    for mod in mods:

        text += (
            f"🚗 {mod[1]}\n"
            f"🎮 {mod[2]}\n"
            f"/mod_{mod[0]}\n\n"
        )


    bot.send_message(
        call.message.chat.id,
        text
    )



# =========================
# Show Mod
# =========================

@bot.message_handler(
    commands=["mod"]
)
def show_mod(message):

    mod_id = message.text.replace(
        "/mod",
        ""
    )

    if not mod_id:
        return


    cursor.execute(
        """
        SELECT name,game,photo,
        description,file_id
        FROM mods
        WHERE id=?
        """,
        (mod_id,)
    )

    mod = cursor.fetchone()


    if not mod:

        bot.send_message(
            message.chat.id,
            "❌ مود پیدا نشد"
        )

        return


    name, game, photo, desc, file_id = mod


    markup = telebot.types.InlineKeyboardMarkup()

    btn = telebot.types.InlineKeyboardButton(
        "⬇️ دانلود",
        callback_data=f"download_{mod_id}"
    )

    markup.add(btn)


    bot.send_photo(
        message.chat.id,
        photo,
        caption=f"""
🚗 {name}

🎮 بازی:
{game}

📝 توضیحات:
{desc}

🔥 Onyx Street
""",
        reply_markup=markup
    )

# =========================
# Admin Add Mod System
# =========================

adding = {}


@bot.message_handler(commands=["admin"])
def admin_panel(message):

    if message.from_user.id != ADMIN_ID:
        return

    markup = telebot.types.InlineKeyboardMarkup()

    add = telebot.types.InlineKeyboardButton(
        "➕ افزودن مود",
        callback_data="add_mod"
    )

    stats = telebot.types.InlineKeyboardButton(
        "📊 آمار",
        callback_data="admin_stats"
    )

    markup.add(add)
    markup.add(stats)

    bot.send_message(
        message.chat.id,
        "🛠 پنل مدیریت Onyx Street",
        reply_markup=markup
    )



@bot.callback_query_handler(
    func=lambda call: call.data == "add_mod"
)
def add_mod_start(call):

    if call.from_user.id != ADMIN_ID:
        return

    adding[call.message.chat.id] = {}

    bot.send_message(
        call.message.chat.id,
        "🚗 اسم مود را ارسال کن:"
    )

    bot.register_next_step_handler(
        call.message,
        get_mod_name
    )



def get_mod_name(message):

    adding[message.chat.id]["name"] = message.text

    bot.send_message(
        message.chat.id,
        "🎮 اسم بازی را ارسال کن:\n\nمثال:\nAssetto Corsa"
    )

    bot.register_next_step_handler(
        message,
        get_mod_game
    )



def get_mod_game(message):

    adding[message.chat.id]["game"] = message.text

    bot.send_message(
        message.chat.id,
        "🖼 عکس مود را ارسال کن:"
    )

    bot.register_next_step_handler(
        message,
        get_mod_photo
    )



def get_mod_photo(message):

    if not message.photo:

        bot.send_message(
            message.chat.id,
            "❌ لطفاً عکس ارسال کن"
        )

        return

    adding[message.chat.id]["photo"] = (
        message.photo[-1].file_id
    )


    bot.send_message(
        message.chat.id,
        "📝 توضیحات مود را ارسال کن:"
    )

    bot.register_next_step_handler(
        message,
        get_mod_description
    )



def get_mod_description(message):

    adding[message.chat.id]["description"] = message.text


    bot.send_message(
        message.chat.id,
        "📦 فایل مود را ارسال کن (ZIP/RAR):"
    )


    bot.register_next_step_handler(
        message,
        get_mod_file
    )



def get_mod_file(message):

    if not message.document:

        bot.send_message(
            message.chat.id,
            "❌ فایل ارسال نشده"
        )

        return


    adding[message.chat.id]["file_id"] = (
        message.document.file_id
    )


    data = adding[message.chat.id]


    cursor.execute(
        """
        INSERT INTO mods
        (
        name,
        game,
        photo,
        description,
        file_id,
        date
        )
        VALUES(?,?,?,?,?,?)
        """,
        (
            data["name"],
            data["game"],
            data["photo"],
            data["description"],
            data["file_id"],
            str(datetime.now())
        )
    )


    db.commit()


    mod_id = cursor.lastrowid


    bot.send_message(
        message.chat.id,
        f"""
✅ مود ثبت شد

🆔 ID:
{mod_id}

🔗 لینک:
https://t.me/{BOT_USERNAME}?start={mod_id}
"""
    )


    del adding[message.chat.id]



# =========================
# Admin Stats
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "admin_stats"
)
def admin_stats(call):

    if call.from_user.id != ADMIN_ID:
        return


    cursor.execute(
        "SELECT COUNT(*) FROM mods"
    )

    mods = cursor.fetchone()[0]


    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    users = cursor.fetchone()[0]


    bot.send_message(
        call.message.chat.id,
        f"""
📊 آمار Onyx Street

👤 کاربران:
{users}

🚗 تعداد مودها:
{mods}
"""
               )

# =========================
# Download System
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("download_")
)
def download_mod(call):

    mod_id = call.data.replace(
        "download_",
        ""
    )

    cursor.execute(
        """
        SELECT file_id
        FROM mods
        WHERE id=?
        """,
        (mod_id,)
    )

    result = cursor.fetchone()

    if not result:
        bot.answer_callback_query(
            call.id,
            "مود پیدا نشد ❌"
        )
        return


    file_id = result[0]


    cursor.execute(
        """
        UPDATE mods
        SET downloads = downloads + 1
        WHERE id=?
        """,
        (mod_id,)
    )

    db.commit()


    bot.answer_callback_query(
        call.id,
        "در حال ارسال فایل..."
    )


    bot.send_document(
        call.message.chat.id,
        file_id,
        caption="⬇️ دانلود شد\n🔥 Onyx Street"
    )



# =========================
# Search System
# =========================

@bot.message_handler(commands=["search"])
def search_start(message):

    bot.send_message(
        message.chat.id,
        "🔎 اسم مود یا بازی را ارسال کنید:"
    )

    bot.register_next_step_handler(
        message,
        search_mod
    )



def search_mod(message):

    keyword = message.text


    cursor.execute(
        """
        SELECT id,name,game
        FROM mods
        WHERE name LIKE ?
        OR game LIKE ?
        LIMIT 10
        """,
        (
            f"%{keyword}%",
            f"%{keyword}%"
        )
    )


    results = cursor.fetchall()


    if not results:

        bot.send_message(
            message.chat.id,
            "❌ چیزی پیدا نشد"
        )

        return


    text = "🔎 نتایج جستجو:\n\n"


    for item in results:

        text += (
            f"🚗 {item[1]}\n"
            f"🎮 {item[2]}\n"
            f"/mod{item[0]}\n\n"
        )


    bot.send_message(
        message.chat.id,
        text
    )



# =========================
# Popular Mods
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "popular"
)
def popular(call):

    cursor.execute(
        """
        SELECT id,name,downloads
        FROM mods
        ORDER BY downloads DESC
        LIMIT 10
        """
    )


    mods = cursor.fetchall()


    text = "⭐ محبوب‌ترین مودها:\n\n"


    for mod in mods:

        text += (
            f"🚗 {mod[1]}\n"
            f"⬇️ دانلود: {mod[2]}\n"
            f"/mod{mod[0]}\n\n"
        )


    bot.send_message(
        call.message.chat.id,
        text
    )
bot.infinity_polling()
