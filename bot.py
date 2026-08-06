import telebot
import sqlite3

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"

ADMIN_ID = 8356358583

CHANNEL = "@OnyxStreet"
CHANNEL_LINK = "https://t.me/OnyxStreet"

bot = telebot.TeleBot(TOKEN)

db = sqlite3.connect("links.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY,
    url TEXT
)
""")
db.commit()


def check_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


@bot.message_handler(commands=["start"])
def start(message):

    if not check_membership(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()

        join = telebot.types.InlineKeyboardButton(
            "📢 عضویت در کانال",
            url=CHANNEL_LINK
        )

        check = telebot.types.InlineKeyboardButton(
            "✅ بررسی عضویت",
            callback_data="check_join"
        )

        markup.add(join)
        markup.add(check)

        bot.send_message(
            message.chat.id,
            "⚠️ برای استفاده از ربات ابتدا عضو کانال شوید:",
            reply_markup=markup
        )
        return


    args = message.text.split()

    if len(args) > 1:
        code = args[1]

        cursor.execute(
            "SELECT url FROM links WHERE id=?",
            (code,)
        )

        result = cursor.fetchone()

        if result:
            bot.send_message(
                message.chat.id,
                f"📦 لینک دانلود مود:\n\n{result[0]}"
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ لینک پیدا نشد"
            )

    else:
        bot.send_message(
            message.chat.id,
            "سلام 👋\nبه Onyx Street خوش آمدید 🚗"
        )


@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):

    if check_membership(call.from_user.id):
        bot.answer_callback_query(
            call.id,
            "عضویت تایید شد ✅"
        )

        bot.send_message(
            call.message.chat.id,
            "✅ دسترسی شما فعال شد"
        )

    else:
        bot.answer_callback_query(
            call.id,
            "هنوز عضو کانال نیستید ❌"
        )


@bot.message_handler(commands=["add"])
def add_link(message):

    if message.from_user.id != ADMIN_ID:
        return

    url = message.text.replace("/add ", "")

    cursor.execute(
        "INSERT INTO links(url) VALUES(?)",
        (url,)
    )

    db.commit()

    code = cursor.lastrowid

    bot.send_message(
        message.chat.id,
        f"✅ ذخیره شد\n\n"
        f"لینک دانلود:\n"
        f"https://t.me/OnyxStreetBot?start={code}"
    )


@bot.message_handler(commands=["admin"])
def admin_panel(message):

    if message.from_user.id != ADMIN_ID:
        return

    markup = telebot.types.InlineKeyboardMarkup()

    stats = telebot.types.InlineKeyboardButton(
        "📊 آمار لینک‌ها",
        callback_data="stats"
    )

    markup.add(stats)

    bot.send_message(
        message.chat.id,
        "🛠 پنل مدیریت Onyx Street",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "stats")
def stats(call):

    if call.from_user.id != ADMIN_ID:
        return

    cursor.execute(
        "SELECT COUNT(*) FROM links"
    )

    count = cursor.fetchone()[0]

    bot.send_message(
        call.message.chat.id,
        f"📦 تعداد لینک‌های ثبت شده: {count}"
    )


bot.infinity_polling()
