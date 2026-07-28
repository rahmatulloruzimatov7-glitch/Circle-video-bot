"""
UMRA SAFARI UCHUN MA'LUMOT YIG'UVCHI TELEGRAM BOT
====================================================
Bu bot foydalanuvchidan Umra safari uchun kerakli ma'lumotlarni
bosqichma-bosqich so'rab, SQLite bazaga saqlaydi va adminga xabar yuboradi.

O'RNATISH:
    pip install pyTelegramBotAPI

ISHGA TUSHIRISH:
    python umra_bot.py
"""

import os
import sqlite3
import telebot
from telebot import types

# ============ SOZLAMALAR ============
# Avval "muhit o'zgaruvchisi" (environment variable)dan o'qishga harakat qiladi
# (bu server uchun xavfsizroq usul). Agar topilmasa, pastdagi qiymatlardan foydalanadi
# — bu kompyuterda mahalliy sinov uchun qulay.
BOT_TOKEN = os.environ.get("BOT_TOKEN", "SIZNING_BOT_TOKENINGIZ")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))
# ======================================

bot = telebot.TeleBot(BOT_TOKEN)

# ---------- Bazani sozlash ----------
conn = sqlite3.connect('umra_malumotlari.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS malumotlar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    ism_familiya TEXT,
    telefon TEXT,
    pasport TEXT,
    tugilgan_sana TEXT,
    safar_sanasi TEXT,
    paket_turi TEXT,
    sana TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# ---------- Holatlarni saqlash uchun xotira ----------
user_data = {}
user_state = {}

STATES = {
    'ISM': 1,
    'TELEFON': 2,
    'PASPORT': 3,
    'TUGILGAN_SANA': 4,
    'SAFAR_SANASI': 5,
    'PAKET': 6,
}


# ---------- /start ----------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_data[user_id] = {}
    user_state[user_id] = STATES['ISM']
    bot.send_message(
        user_id,
        "Assalomu alaykum! 🕋\n\n"
        "Umra safari uchun ariza topshirish botiga xush kelibsiz.\n"
        "Quyidagi ma'lumotlarni to'ldirishingizni so'raymiz.\n\n"
        "Ism va familiyangizni kiriting:"
    )


# ---------- Ism-familiya ----------
@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == STATES['ISM'])
def get_ism(message):
    user_id = message.from_user.id
    user_data[user_id]['ism_familiya'] = message.text
    user_state[user_id] = STATES['TELEFON']

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton("📱 Raqamni yuborish", request_contact=True))
    bot.send_message(user_id, "Telefon raqamingizni yuboring:", reply_markup=keyboard)


# ---------- Telefon (kontakt orqali) ----------
@bot.message_handler(content_types=['contact'], func=lambda m: user_state.get(m.from_user.id) == STATES['TELEFON'])
def get_telefon_contact(message):
    user_id = message.from_user.id
    user_data[user_id]['telefon'] = message.contact.phone_number
    ask_pasport(user_id)


# ---------- Telefon (qo'lda yozilsa) ----------
@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == STATES['TELEFON'])
def get_telefon_text(message):
    user_id = message.from_user.id
    user_data[user_id]['telefon'] = message.text
    ask_pasport(user_id)


def ask_pasport(user_id):
    user_state[user_id] = STATES['PASPORT']
    bot.send_message(
        user_id,
        "Pasport seriya va raqamingizni kiriting (masalan: AB1234567):",
        reply_markup=types.ReplyKeyboardRemove()
    )


# ---------- Pasport ----------
@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == STATES['PASPORT'])
def get_pasport(message):
    user_id = message.from_user.id
    user_data[user_id]['pasport'] = message.text
    user_state[user_id] = STATES['TUGILGAN_SANA']
    bot.send_message(user_id, "Tug'ilgan sanangizni kiriting (kun.oy.yil, masalan: 15.03.1990):")


# ---------- Tug'ilgan sana ----------
@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == STATES['TUGILGAN_SANA'])
def get_tugilgan_sana(message):
    user_id = message.from_user.id
    user_data[user_id]['tugilgan_sana'] = message.text
    user_state[user_id] = STATES['SAFAR_SANASI']
    bot.send_message(user_id, "Qaysi oyda Umraga borishni xohlaysiz? (masalan: 2026-yil oktabr):")


# ---------- Safar sanasi ----------
@bot.message_handler(func=lambda m: user_state.get(m.from_user.id) == STATES['SAFAR_SANASI'])
def get_safar_sanasi(message):
    user_id = message.from_user.id
    user_data[user_id]['safar_sanasi'] = message.text
    user_state[user_id] = STATES['PAKET']

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("💰 Iqtisodiy", callback_data="paket_iqtisodiy"))
    keyboard.add(types.InlineKeyboardButton("⭐ Standart", callback_data="paket_standart"))
    keyboard.add(types.InlineKeyboardButton("👑 VIP", callback_data="paket_vip"))
    bot.send_message(user_id, "Qaysi paket turini tanlaysiz?", reply_markup=keyboard)


# ---------- Paket tanlash va yakunlash ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith('paket_'))
def get_paket(call):
    user_id = call.from_user.id
    paket_nomlari = {
        'paket_iqtisodiy': 'Iqtisodiy',
        'paket_standart': 'Standart',
        'paket_vip': 'VIP'
    }
    user_data[user_id]['paket_turi'] = paket_nomlari[call.data]
    d = user_data[user_id]

    # Bazaga saqlash
    cursor.execute('''
        INSERT INTO malumotlar
        (user_id, ism_familiya, telefon, pasport, tugilgan_sana, safar_sanasi, paket_turi)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, d['ism_familiya'], d['telefon'], d['pasport'],
          d['tugilgan_sana'], d['safar_sanasi'], d['paket_turi']))
    conn.commit()

    xulosa = (
        "✅ Arizangiz qabul qilindi!\n\n"
        f"👤 Ism: {d['ism_familiya']}\n"
        f"📱 Telefon: {d['telefon']}\n"
        f"🛂 Pasport: {d['pasport']}\n"
        f"🎂 Tug'ilgan sana: {d['tugilgan_sana']}\n"
        f"🗓 Safar sanasi: {d['safar_sanasi']}\n"
        f"📦 Paket: {d['paket_turi']}\n\n"
        "Tez orada operatorlarimiz siz bilan bog'lanishadi. Rahmat! 🕋"
    )
    bot.send_message(user_id, xulosa)
    bot.answer_callback_query(call.id)

    # Adminga xabar
    admin_xabar = f"🆕 Yangi ariza!\n\n{xulosa}\n\nUser ID: {user_id}"
    try:
        bot.send_message(ADMIN_ID, admin_xabar)
    except Exception as e:
        print(f"Adminga xabar yuborishda xatolik: {e}")

    user_state[user_id] = None
    user_data[user_id] = {}


# ---------- Admin uchun: barcha arizalarni ko'rish ----------
@bot.message_handler(commands=['malumotlar'])
def show_all(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Bu buyruq faqat admin uchun.")
        return

    cursor.execute('SELECT * FROM malumotlar ORDER BY sana DESC')
    rows = cursor.fetchall()
    if not rows:
        bot.send_message(message.chat.id, "Hozircha ma'lumot yo'q.")
        return

    for row in rows[:20]:
        matn = (
            f"ID: {row[0]}\nIsm: {row[2]}\nTel: {row[3]}\nPasport: {row[4]}\n"
            f"Tug'ilgan: {row[5]}\nSafar: {row[6]}\nPaket: {row[7]}\nSana: {row[8]}\n"
            + "-" * 20
        )
        bot.send_message(message.chat.id, matn)


# ---------- Botni ishga tushirish ----------
if __name__ == '__main__':
    print("Bot ishga tushdi...")
    bot.infinity_polling()
