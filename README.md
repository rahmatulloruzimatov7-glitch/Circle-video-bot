# Kvadrat videoni yumaloq video xabarga aylantiruvchi bot

## Bot nima qiladi?
Foydalanuvchi istalgan videoni yuborsa, bot uni:
1. Kvadrat shaklga kesadi (markazidan)
2. 384x384 o'lchamga moslaydi
3. 60 soniyagacha qisqartiradi (agar uzunroq bo'lsa)
4. Telegramning maxsus "yumaloq video xabar" formatida qaytarib yuboradi

## Cheklovlar (Telegramning o'zi qo'ygan, bepul, lekin o'zgartirib bo'lmaydi)
- Kirish video hajmi: 20 MB dan oshmasligi kerak
- Video davomiyligi: 60 soniyadan uzun bo'lsa, avtomatik qisqartiriladi

## O'rnatish — 2 xil yo'l bor:

### 1-yo'l: Railway'ga joylashtirish (tavsiya etiladi, 24/7 ishlaydi)

1. Yangi Telegram bot yarating (@BotFather orqali, xuddi avvalgidek)
2. Shu papkadagi barcha fayllarni (`yumaloq_video_bot.py`, `Dockerfile`, `requirements.txt`) yangi GitHub repository'ga yuklang
3. Railway'da **"New Project"** → **"Deploy from GitHub repo"** orqali shu repo'ni tanlang
4. Railway avtomatik ravishda `Dockerfile`ni sezib, ffmpeg bilan birga botni quradi (bu odatdagidan biroz ko'proq vaqt olishi mumkin — 2-4 daqiqa)
5. **Variables** bo'limiga `BOT_TOKEN` qo'shing (yangi botning tokeni)

### 2-yo'l: Kompyuterda sinash

1. `ffmpeg`ni kompyuteringizga o'rnating:
   - Windows: [ffmpeg.org/download.html](https://ffmpeg.org/download.html) dan yuklab, PATH'ga qo'shing
   - Yoki (agar Chocolatey bor bo'lsa): `choco install ffmpeg`
2. Kutubxonani o'rnating: `pip install -r requirements.txt`
3. `yumaloq_video_bot.py` faylida `BOT_TOKEN`ni to'ldiring
4. Ishga tushiring: `python yumaloq_video_bot.py`

## Sinab ko'rish

Telegram'da botga istalgan videoni yuboring — bir necha soniyadan so'ng u yumaloq video xabar sifatida qaytishi kerak.
