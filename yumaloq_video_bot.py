"""
KVADRAT VIDEONI YUMALOQ VIDEO XABARGA AYLANTIRUVCHI TELEGRAM BOT
====================================================
Foydalanuvchi istalgan videoni yuborsa, bot uni ffmpeg orqali
kvadrat shaklga keltirib, Telegramning "video xabar" (yumaloq video)
formatida qaytarib yuboradi.

TALAB QILINADIGAN DASTUR: ffmpeg (kompyuterda alohida o'rnatilishi kerak,
Railway'da Dockerfile orqali avtomatik o'rnatiladi).

O'RNATISH (mahalliy kompyuterda sinash uchun):
    pip install pyTelegramBotAPI
    va ffmpeg'ni alohida o'rnatish kerak: https://ffmpeg.org/download.html

ISHGA TUSHIRISH:
    python yumaloq_video_bot.py
"""

import os
import subprocess
import tempfile
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot

# ============ SOZLAMALAR ============
BOT_TOKEN = os.environ.get("BOT_TOKEN", "SIZNING_BOT_TOKENINGIZ")
MAX_DAVOMIYLIK = 60  # soniya -- Telegram video xabarlari odatda shu chegarada
VIDEO_OLCHAMI = 384  # piksel (kengligi = balandligi)
PORT = int(os.environ.get("PORT", 10000))  # Render "Web Service" uchun port talab qiladi
# ======================================

bot = telebot.TeleBot(BOT_TOKEN)


# ---------- Render uchun soxta HTTP server ----------
# Render.com bepul "Web Service"lar biror portni tinglashini talab qiladi,
# aks holda xizmatni "ishlamayapti" deb hisoblaydi. Bu oddiy server shunchaki
# "Bot ishlayapti" deb javob beradi, botning asosiy ishiga aloqasi yo'q.
class SalomatlikTekshiruvi(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot ishlayapti!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def log_message(self, format, *args):
        pass  # Konsolni keraksiz yozuvlar bilan to'ldirmaslik uchun


def http_serverni_ishga_tushirish():
    server = HTTPServer(('0.0.0.0', PORT), SalomatlikTekshiruvi)
    server.serve_forever()


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Salom! 🎥\n\n"
        "Menga istalgan (kvadrat yoki to'rtburchak) videoni yuboring — "
        "men uni Telegramning yumaloq video xabariga aylantirib beraman.\n\n"
        "⚠️ Eslatma: video hajmi 20 MB dan oshmasligi, davomiyligi esa "
        f"{MAX_DAVOMIYLIK} soniyadan oshmasligi kerak (uzunroq bo'lsa, "
        "avtomatik qisqartiriladi)."
    )


@bot.message_handler(content_types=['video', 'document'])
def handle_video(message):
    file_id = None

    if message.content_type == 'video':
        file_id = message.video.file_id
    elif message.content_type == 'document' and message.document.mime_type and 'video' in message.document.mime_type:
        file_id = message.document.file_id
    else:
        bot.reply_to(message, "Iltimos, video fayl yuboring. 🎥")
        return

    processing_msg = bot.reply_to(message, "⏳ Video qayta ishlanmoqda, biroz kuting...")

    with tempfile.TemporaryDirectory() as tmpdir:
        kirish_fayl = os.path.join(tmpdir, "kirish.mp4")
        chiqish_fayl = os.path.join(tmpdir, "chiqish.mp4")

        # 1) Videoni Telegramdan yuklab olish
        try:
            file_info = bot.get_file(file_id)
            downloaded = bot.download_file(file_info.file_path)
            with open(kirish_fayl, 'wb') as f:
                f.write(downloaded)
        except Exception:
            bot.edit_message_text(
                "❌ Videoni yuklab olishda xatolik. Ehtimol, fayl juda katta "
                "(20 MB dan oshmasligi kerak).",
                message.chat.id, processing_msg.message_id
            )
            return

        # 2) ffmpeg orqali kvadrat qilib kesish + o'lchamini moslash + davomiylikni cheklash
        cmd = [
            "ffmpeg", "-y", "-i", kirish_fayl,
            "-t", str(MAX_DAVOMIYLIK),
            "-vf", f"crop='min(iw,ih)':'min(iw,ih)',scale={VIDEO_OLCHAMI}:{VIDEO_OLCHAMI}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            chiqish_fayl
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=120)
        except subprocess.CalledProcessError as e:
            bot.edit_message_text("❌ Videoni qayta ishlashda xatolik yuz berdi.",
                                   message.chat.id, processing_msg.message_id)
            print(f"ffmpeg xatosi: {e.stderr}")
            return
        except subprocess.TimeoutExpired:
            bot.edit_message_text("❌ Video juda uzun, qayta ishlash vaqti tugadi.",
                                   message.chat.id, processing_msg.message_id)
            return
        except FileNotFoundError:
            bot.edit_message_text(
                "❌ Serverda ffmpeg topilmadi. Administratorga xabar bering.",
                message.chat.id, processing_msg.message_id
            )
            return

        # 3) Yumaloq video xabar sifatida yuborish
        try:
            with open(chiqish_fayl, 'rb') as video_note:
                bot.send_video_note(message.chat.id, video_note, length=VIDEO_OLCHAMI)
            bot.delete_message(message.chat.id, processing_msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Yumaloq videoni yuborishda xatolik: {e}",
                                   message.chat.id, processing_msg.message_id)


@bot.message_handler(func=lambda m: True, content_types=['text'])
def fallback(message):
    if message.text and message.text.startswith('/'):
        return
    bot.reply_to(message, "Menga video yuboring — men uni yumaloq video xabariga aylantirib beraman. 🎥")


if __name__ == '__main__':
    # HTTP serverni fon rejimida (alohida oqimda) ishga tushiramiz
    http_thread = threading.Thread(target=http_serverni_ishga_tushirish, daemon=True)
    http_thread.start()

    print("Bot ishga tushdi...")
    bot.infinity_polling()
