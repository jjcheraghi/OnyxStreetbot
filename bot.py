import telebot
import sqlite3

TOKEN = "8926088350:AAElvXxA3gADwdLbEFxyZ3WIiyIi0qow74Q"
ADMIN_ID = 8356358583
CHANNEL = "@GTAOnyx"

bot = telebot.TeleBot(TOKEN)

db = sqlite3.connect("mods.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS mods(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
file_id TEXT
)
""")

db.commit()


def is_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status != "left"
    except:
        return False



@bot.message_handler(commands=["start"])
def start(message):

    args = message.text.split()

    if len(args) > 1:

        if args[1].startswith("mod_"):

            mod_id = args[1].replace("mod_", "")

            cur.execute(
                "SELECT name,file_id FROM mods WHERE id=?",
                (mod_id,)
            )

            mod = cur.fetchone()

            if mod:

                if not is_joined(message.from_user.id):
                    bot.reply_to(
                        message,
                        f"ابتدا عضو کانال شوید:\n{CHANNEL}"
                    )
                    return


                bot.send_document(
                    message.chat.id,
                    mod[1],
                    caption=f"{mod[0]}\n\nGTA ONYX"
                )

                return


    bot.reply_to(
        message,
        "به GTA ONYX Bot خوش آمدید.\n\n/mods"
    )



@bot.message_handler(commands=["mods"])
def mods(message):

    if message.from_user.id == ADMIN_ID:

        cur.execute(
            "SELECT id,name FROM mods"
        )

        data = cur.fetchall()

        text="لیست مودها:\n\n"

        for m in data:
            text += f"{m[0]} | {m[1]}\n"

        bot.reply_to(message,text)

    else:

        bot.reply_to(
            message,
            "برای دریافت مود از لینک اختصاصی استفاده کنید."
        )



@bot.message_handler(commands=["panel"])
def panel(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.reply_to(
        message,
        """
پنل GTA ONYX

/add - اضافه کردن مود
/del - حذف مود
/mods - لیست مودها
"""
    )



@bot.message_handler(commands=["add"])
def add(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.reply_to(
        message,
        "فایل مود را ارسال کن."
    )

    bot.register_next_step_handler(
        message,
        get_file
    )



def get_file(message):

    if not message.document:
        return

    file_id = message.document.file_id

    bot.reply_to(
        message,
        "اسم مود را ارسال کن."
    )

    bot.register_next_step_handler(
        message,
        save_mod,
        file_id
    )



def save_mod(message,file_id):

    name = message.text

    cur.execute(
        "INSERT INTO mods(name,file_id) VALUES(?,?)",
        (name,file_id)
    )

    db.commit()

    mod_id = cur.lastrowid

    username = bot.get_me().username

    link = f"https://t.me/{username}?start=mod_{mod_id}"


    bot.reply_to(
        message,
        f"""
مود ذخیره شد.

نام:
{name}

لینک اختصاصی:
{link}
"""
    )



@bot.message_handler(commands=["del"])
def delete(message):

    if message.from_user.id != ADMIN_ID:
        return


    try:

        mod_id = message.text.split()[1]

        cur.execute(
            "DELETE FROM mods WHERE id=?",
            (mod_id,)
        )

        db.commit()


        bot.reply_to(
            message,
            "مود حذف شد."
        )

    except:

        bot.reply_to(
            message,
            "مثال:
/del 3"
        )



print("GTA ONYX BOT STARTED")

bot.infinity_polling()
