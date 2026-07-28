# Umra safari — ma'lumot yig'uvchi Telegram bot

## Bot nima qiladi?
Foydalanuvchidan bosqichma-bosqich quyidagi ma'lumotlarni so'raydi:
1. Ism-familiya
2. Telefon raqami (tugma orqali yoki qo'lda)
3. Pasport seriya/raqami
4. Tug'ilgan sana
5. Safar qilmoqchi bo'lgan sana/oy
6. Paket turi (Iqtisodiy / Standart / VIP — tugmalar orqali)

Barcha ma'lumotlar `umra_malumotlari.db` (SQLite) fayliga saqlanadi va admin darhol xabar oladi.

## O'rnatish

1. Python 3.9+ o'rnatilgan bo'lishi kerak.
2. Kerakli kutubxonani o'rnating:
   ```
   pip install -r requirements.txt
   ```

## Sozlash

`umra_bot.py` faylini oching va tepasidagi ikkita qatorni to'ldiring:

```python
BOT_TOKEN = "SIZNING_BOT_TOKENINGIZ"   # @BotFather'dan olinadi
ADMIN_ID = 123456789                    # Sizning Telegram ID'ingiz
```

- **BOT_TOKEN**: Telegram'da @BotFather ga yozib, `/newbot` orqali oling.
- **ADMIN_ID**: Telegram'da @userinfobot ga yozing, u sizning ID raqamingizni beradi.

## Ishga tushirish

```
python umra_bot.py
```

Terminalda "Bot ishga tushdi..." yozuvi chiqsa, bot ishlayapti. Telegram'da botingizni topib `/start` deb yozing.

## Admin buyruqlari

- `/malumotlar` — barcha qabul qilingan arizalarni ko'rsatadi (faqat ADMIN_ID uchun ishlaydi).

## Keyingi qadamlar (tavsiyalar)

- **24/7 ishlashi uchun**: botni VPS, Railway, yoki Render kabi serverga joylashtiring.
- **Excel eksport**: arizalarni Excel faylga chiqarish funksiyasini qo'shish mumkin.
- **Validatsiya**: telefon raqami va pasport formatini tekshirish (regex orqali) qo'shish tavsiya etiladi.
- **Ko'p tilli qo'llab-quvvatlash**: rus/ingliz tillarini qo'shish mumkin.
- **To'lov integratsiyasi**: Click, Payme kabi to'lov tizimlarini ulash mumkin.

Agar shu funksiyalardan birortasini qo'shishni xohlasangiz, ayting — kodni kengaytirib beraman.
