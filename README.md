# @msliderbot — Muhriddin Qarshiyev Referral Bot

## Faylllar
| Fayl | Tavsif |
|------|--------|
| `bot.py` | Asosiy bot kodi |
| `database.py` | SQLite ma'lumotlar bazasi |
| `requirements.txt` | Python kutubxonalari |
| `render.yaml` | Render.com konfiguratsiyasi |

## Render.com ga deploy qilish

1. GitHub repoga yuklang (barcha fayllarni)
2. [render.com](https://render.com) ga kiring → **New → Blueprint**
3. Reponi tanlang — `render.yaml` avtomatik aniqlanadi
4. **Environment Variables** bo'limiga quyidagini qo'shing:

| O'zgaruvchi | Qiymat |
|-------------|--------|
| `BOT_TOKEN` | BotFather'dan olingan token |

5. **Deploy** tugmasini bosing.

## Telegram sozlamalari (muhim!)

### BotFather:
```
/setjoingroups  → Enable
/setprivacy     → Disable  (guruh xabarlarini o'qish uchun)
```

### 2-kanal uchun join request:
- Botni 2-kanal adminlari orasiga qo'shing
- Kanalda "Join Requests" yoqilgan bo'lishi kerak

### Sovg'a kanali (-1003763206013):
- Botni ushbu kanalga **admin** qilib qo'shing
- "Invite Users" ruxsatini bering

## Admin buyruqlari
| Buyruq | Tavsif |
|--------|--------|
| `/panel` | Admin panel |
| `/odam` | Foydalanuvchilar soni |
| `/xabar <matn>` | Hammaga xabar yuborish |
