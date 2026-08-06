import telebot
import sqlite3
from datetime import datetime

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"

ADMIN_ID = 8356358583

CHANNEL = "@Onyx_Street"
CHANNEL_LINK = "https://t.me/Onyx_Street"

bot = telebot.TeleBot(TOKEN)


db = sqlite3.connect(
    "onyx.db",
    check_same_thread=False
)

cursor = db.cursor()


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


db.commit()


adding = {}



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



def join_keyboard():

    markup = telebot.types.InlineKeyboardMarkup()

    markup.add(
        telebot.types.InlineKeyboardButton(
            "📢 عضویت در کانال",
            url=CHANNEL_LINK
        )
    )

    markup.add(
        telebot.types.InlineKeyboardButton(
            "✅ بررسی عضویت",
            callback_data="check_join"
        )
    )

    return markup



def main_menu():

    markup = telebot.types.InlineKeyboardMarkup(
        row_width=2
    )

    markup.add(
        telebot.types.InlineKeyboardButton(
            "🔥 جدیدترین مودها",
            callback_data="latest"
        ),
        telebot.types.InlineKeyboardButton(
            "🎮 بازی‌ها",
            callback_data="games"
        )
    )

    markup.add(
        telebot.types.InlineKeyboardButton(
            "🔎 جستجو",
            callback_data="search"
        ),
        telebot.types.InlineKeyboardButton(
            "📢 کانال",
            url=CHANNEL_LINK
        )
    )

    return markup



@bot.message_handler(commands=["start"])
def start(message):

    if not check_membership(
        message.from_user.id
    ):

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



@bot.callback_query_handler(
    func=lambda call: call.data=="check_join"
)
def check_join(call):

    if check_membership(
        call.from_user.id
    ):

        bot.answer_callback_query(
            call.id,
            "عضویت تایید شد ✅"
        )

        bot.send_message(
            call.message.chat.id,
            "✅ حالا /start را بزنید"
        )

    else:

        bot.answer_callback_query(
            call.id,
            "هنوز عضو نیستید ❌"
)
# =========================
# Game Categories
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "games"
)
def games(call):

    markup = telebot.types.InlineKeyboardMarkup()

    games_list = [
        ("🏎 Assetto Corsa", "Assetto Corsa"),
        ("🚙 BeamNG Drive", "BeamNG"),
        ("🚘 GTA V", "GTA V"),
        ("🏙 GTA San Andreas", "GTA SA"),
        ("🚛 ETS2", "ETS2"),
        ("🚚 ATS", "ATS"),
        ("🏁 NFS Most Wanted 2012", "NFS MW 2012")
    ]

    for name, data in games_list:

        markup.add(
            telebot.types.InlineKeyboardButton(
                name,
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


    markup = telebot.types.InlineKeyboardMarkup()

    for mod in mods:

        markup.add(
            telebot.types.InlineKeyboardButton(
                f"🚗 {mod[1]}",
                callback_data=f"show_{mod[0]}"
            )
        )


    bot.send_message(
        call.message.chat.id,
        "🔥 جدیدترین مودها:",
        reply_markup=markup
    )



# =========================
# Show Mod
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("show_")
)
def show_mod(call):

    mod_id = call.data.replace(
        "show_",
        ""
    )

    cursor.execute(
        """
        SELECT name,game,photo,description,file_id,downloads
        FROM mods
        WHERE id=?
        """,
        (mod_id,)
    )

    mod = cursor.fetchone()


    if not mod:

        return


    name, game, photo, desc, file_id, downloads = mod


    markup = telebot.types.InlineKeyboardMarkup()

    markup.add(
        telebot.types.InlineKeyboardButton(
            "⬇️ دانلود مود",
            callback_data=f"download_{mod_id}"
        )
    )


    bot.send_photo(
        call.message.chat.id,
        photo,
        caption=f"""
🚗 {name}

🎮 بازی:
{game}

📝 توضیحات:
{desc}

⬇️ دانلودها:
{downloads}
""",
        reply_markup=markup
    )



# =========================
# Download File
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("download_")
)
def download(call):

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


    bot.send_document(
        call.message.chat.id,
        file_id,
        caption="🔥 Onyx Street\n⬇️ دانلود شد"
    )
