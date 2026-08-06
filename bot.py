import telebot
import sqlite3

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"

ADMIN_ID = 8356358583

CHANNEL = "@Onyx_Street"
CHANNEL_LINK = "https://t.me/Onyx_Street"

bot = telebot.TeleBot(TOKEN)


# =====================
# DATABASE
# =====================

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
    downloads INTEGER DEFAULT 0
)
""")


db.commit()


# ذخیره اطلاعات موقت ادمین
adding = {}



# =====================
# JOIN CHECK
# =====================

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

    kb = telebot.types.InlineKeyboardMarkup()

    kb.add(
        telebot.types.InlineKeyboardButton(
            "📢 عضویت در کانال",
            url=CHANNEL_LINK
        )
    )

    kb.add(
        telebot.types.InlineKeyboardButton(
            "✅ بررسی عضویت",
            callback_data="check_join"
        )
    )

    return kb



# =====================
# MAIN MENU
# =====================

def main_menu():

    kb = telebot.types.InlineKeyboardMarkup(
        row_width=2
    )


    kb.add(
        telebot.types.InlineKeyboardButton(
            "🔥 جدیدترین مودها",
            callback_data="latest"
        ),

        telebot.types.InlineKeyboardButton(
            "🎮 بازی‌ها",
            callback_data="games"
        )
    )


    kb.add(
        telebot.types.InlineKeyboardButton(
            "🔎 جستجو",
            callback_data="search"
        ),

        telebot.types.InlineKeyboardButton(
            "📢 کانال",
            url=CHANNEL_LINK
        )
    )


    return kb



# =====================
# START
# =====================

@bot.message_handler(
    commands=["start"]
)
def start(message):

    if not check_join(
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



# =====================
# CHECK JOIN BUTTON
# =====================

@bot.callback_query_handler(
    func=lambda call: call.data=="check_join"
)
def check_join_button(call):

    if check_join(
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
            "هنوز عضو کانال نیستید ❌"
        )
# =====================
# ADMIN PANEL
# =====================

@bot.message_handler(
    commands=["admin"]
)
def admin_panel(message):

    if message.from_user.id != ADMIN_ID:
        return


    kb = telebot.types.InlineKeyboardMarkup()


    kb.add(
        telebot.types.InlineKeyboardButton(
            "➕ افزودن مود",
            callback_data="add_mod"
        )
    )


    kb.add(
        telebot.types.InlineKeyboardButton(
            "📊 آمار",
            callback_data="stats"
        )
    )


    bot.send_message(
        message.chat.id,
        "🛠 پنل مدیریت Onyx Street",
        reply_markup=kb
    )



# =====================
# ADD MOD START
# =====================

@bot.callback_query_handler(
    func=lambda call: call.data=="add_mod"
)
def add_mod(call):

    if call.from_user.id != ADMIN_ID:
        return


    adding[call.message.chat.id] = {}


    bot.send_message(
        call.message.chat.id,
        "🚗 نام مود را ارسال کن:"
    )


    bot.register_next_step_handler(
        call.message,
        get_name
    )



def get_name(message):

    adding[message.chat.id]["name"] = message.text


    bot.send_message(
        message.chat.id,
        "🎮 نام بازی را ارسال کن:\nمثال: NFS Most Wanted 2012"
    )


    bot.register_next_step_handler(
        message,
        get_game
    )



def get_game(message):

    adding[message.chat.id]["game"] = message.text


    bot.send_message(
        message.chat.id,
        "🖼 عکس مود را ارسال کن:"
    )


    bot.register_next_step_handler(
        message,
        get_photo
    )



def get_photo(message):

    if not message.photo:

        bot.send_message(
            message.chat.id,
            "❌ فقط عکس ارسال کن"
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
        get_description
    )



def get_description(message):

    adding[message.chat.id]["description"] = message.text


    bot.send_message(
        message.chat.id,
        "📦 فایل مود را ارسال کن (ZIP/RAR):"
    )


    bot.register_next_step_handler(
        message,
        get_file
    )



def get_file(message):

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
        file_id
        )
        VALUES (?,?,?,?,?)
        """,

        (
            data["name"],
            data["game"],
            data["photo"],
            data["description"],
            data["file_id"]
        )
    )


    db.commit()


    bot.send_message(
        message.chat.id,
        "✅ مود با
