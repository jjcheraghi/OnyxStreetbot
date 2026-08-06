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
