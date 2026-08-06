import telebot
import sqlite3

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"

ADMIN_ID = 8356358583

CHANNEL = "@Onyx_Street"
CHANNEL_LINK = "https://t.me/Onyx_Street"

BOT_USERNAME = "OnyxStreetBot"

bot = telebot.TeleBot(TOKEN)

db = sqlite3.connect("links.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS mods (
    id INTEGER PRIMARY KEY,
    name TEXT,
    photo TEXT,
    description TEXT,
    url TEXT
)
""")
db.commit()


waiting = {}


def check_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# Start
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
            "⚠️ ابتدا عضو کانال شوید:",
            reply_markup=markup
        )
        return


    args = message.text.split()

    if len(args) > 1:

        mod_id = args[1]

        cursor.execute(
            "SELECT name, photo, description, url FROM mods WHERE id=?",
            (mod_id,)
        )

        mod = cursor.fetchone()

        if mod:

            name, photo, description, url = mod

            markup = telebot.types.InlineKeyboardMarkup()

            btn = telebot.types.InlineKeyboardButton(
                "⬇️ دانلود مود",
                url=url
            )

            markup.add(btn)

            bot.send_photo(
                message.chat.id,
                photo,
                caption=f"""
🚗 {name}

📝 توضیحات:
{description}

🔥 Onyx Street
""",
                reply_markup=markup
            )

        else:
            bot.send_message(
                message.chat.id,
                "❌ مود پیدا نشد"
            )

    else:

        bot.send_message(
            message.chat.id,
            "سلام 👋\nبه Onyx Street خوش آمدید 🚗"
        )


# Check join
@bot.callback_query_handler(func=lambda call: call.data=="check_join")
def check_join(call):

    if check_membership(call.from_user.id):
        bot.answer_callback_query(
            call.id,
            "عضویت تایید شد ✅"
        )

        bot.send_message(
            call.message.chat.id,
            "✅ حالا می‌توانید از ربات استفاده کنید"
        )

    else:
        bot.answer_callback_query(
            call.id,
            "هنوز عضو کانال نیستید ❌"
        )


# Add mod
@bot.message_handler(commands=["add"])
def add_mod(message):

    if message.from_user.id != ADMIN_ID:
        return

    waiting[message.chat.id] = {}

    bot.send_message(
        message.chat.id,
        "🚗 اسم مود را ارسال کن:"
    )

    bot.register_next_step_handler(
        message,
        get_name
    )


def get_name(message):

    waiting[message.chat.id]["name"] = message.text

    bot.send_message(
        message.chat.id,
        "🖼 عکس مود را ارسال کن:"
    )

    bot.register_next_step_handler(
        message,
        get_photo
    )


def get_photo(message):

    waiting[message.chat.id]["photo"] = message.photo[-1].file_id

    bot.send_message(
        message.chat.id,
        "📝 توضیحات مود:"
    )

    bot.register_next_step_handler(
        message,
        get_description
    )


def get_description(message):

    waiting[message.chat.id]["description"] = message.text

    bot.send_message(
        message.chat.id,
        "🔗 لینک دانلود:"
    )

    bot.register_next_step_handler(
        message,
        save_mod
    )


def save_mod(message):

    data = waiting[message.chat.id]

    cursor.execute(
        """
        INSERT INTO mods(name,photo,description,url)
        VALUES(?,?,?,?)
        """,
        (
            data["name"],
            data["photo"],
            data["description"],
            message.text
        )
    )

    db.commit()

    mod_id = cursor.lastrowid

    bot.send_message(
        message.chat.id,
        f"""
✅ مود ذخیره شد

🔗 لینک:
https://t.me/{BOT_USERNAME}?start={mod_id}
"""
    )

    del waiting[message.chat.id]


# Admin panel
@bot.message_handler(commands=["admin"])
def admin(message):

    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute(
        "SELECT COUNT(*) FROM mods"
    )

    count = cursor.fetchone()[0]

    bot.send_message(
        message.chat.id,
        f"""
🛠 پنل مدیریت Onyx Street

📦 تعداد مودها: {count}

برای افزودن مود:
 /add
"""
    )


bot.infinity_polling()
