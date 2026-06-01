import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, ChatJoinRequestHandler
)
from telegram.error import TelegramError
from aiohttp import web
import database as db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]   # https://yourapp.onrender.com
PORT = int(os.environ.get("PORT", 10000))

CHANNEL_1 = "@Milliy_sertifikat_lider"
CHANNEL_2_ID = -1003945305522
GIFT_CHANNEL_ID = -1003763206013
ADMIN_IDS = [6987211321, 5523761749]
REQUIRED_REFERRALS = 5

# ─────────────────────────── helpers ────────────────────────────

def subscription_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 1-kanal", url="https://t.me/Milliy_sertifikat_lider")],
        [InlineKeyboardButton("📢 2-kanal (so'rov yuborish)", url="https://t.me/+zfIZNpX9BLplMTBi")],
        [InlineKeyboardButton("✅ Tasdiqlash", callback_data="check_sub")],
    ])

async def check_channel1(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_1, user_id)
        return member.status in ("member", "administrator", "creator")
    except TelegramError:
        return False

async def check_channel2_request(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_2_ID, user_id)
        if member.status in ("member", "administrator", "creator"):
            return True
    except TelegramError:
        pass
    return db.has_join_request(user_id)

# ─────────────────────────── /start ────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or "Do'st"

    db.add_user(user_id, first_name)

    if context.args:
        ref_id_str = context.args[0]
        if ref_id_str.isdigit():
            ref_id = int(ref_id_str)
            if ref_id != user_id and not db.referral_exists(ref_id, user_id):
                db.add_referral(ref_id, user_id)
                count = db.get_referral_count(ref_id)
                remaining = max(0, REQUIRED_REFERRALS - count)
                try:
                    await context.bot.send_message(
                        ref_id,
                        f"🎉 Sizda +1 ta do'st, jami <b>{count}</b> ta, "
                        f"sizga yana <b>{remaining}</b> ta odam kerak!",
                        parse_mode="HTML"
                    )
                    if count >= REQUIRED_REFERRALS and not db.gift_already_notified(ref_id):
                        db.set_gift_notified(ref_id)
                        await context.bot.send_message(
                            ref_id,
                            "🎊 <b>Tabriklaymiz!</b> Endi sovg'ani olishingiz mumkin!",
                            parse_mode="HTML",
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("🎁 Sovg'ani olish", callback_data="get_gift")]
                            ])
                        )
                except TelegramError:
                    pass

    welcome_text = (
        f"Assalomu alaykum <b>{first_name}</b>, botga xush kelibsiz! 🎉\n\n"
        "Bu bot orqali siz <b>Muhriddin Qarshiyev</b>ning Kurslari uchun "
        "<b>50% chegirma</b> va <b>Bepul darslariga</b> ega bo'la olasiz.\n\n"
        "Davom etish uchun quyidagi kanallarga obuna bo'ling 👇"
    )
    await update.message.reply_text(
        welcome_text,
        parse_mode="HTML",
        reply_markup=subscription_keyboard()
    )

# ─────────────────────────── callback: check_sub ────────────────

async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "Do'st"

    in_ch1 = await check_channel1(context.bot, user_id)
    in_ch2 = await check_channel2_request(context.bot, user_id)

    if not in_ch1:
        await query.message.reply_text(
            "❌ Siz hali <b>1-kanalga</b> obuna bo'lmagansiz.\nIltimos, obuna bo'lib qayta tasdiqlang.",
            parse_mode="HTML",
            reply_markup=subscription_keyboard()
        )
        return

    if not in_ch2:
        await query.message.reply_text(
            "❌ Siz hali <b>2-kanalga</b> so'rov yubormagansiz.\n"
            "Iltimos, 2-kanal tugmasini bosib so'rov yuboring va qayta tasdiqlang.",
            parse_mode="HTML",
            reply_markup=subscription_keyboard()
        )
        return

    bot_username = (await context.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={user_id}"
    count = db.get_referral_count(user_id)
    remaining = max(0, REQUIRED_REFERRALS - count)

    text = (
        f"✅ <b>Ajoyib, {first_name}!</b> Barcha talablar bajarildi!\n\n"
        f"🎁 Sovg'ani olish uchun atigi <b>5 ta do'stingizni</b> taklif qiling.\n\n"
        f"👥 Joriy: <b>{count}/{REQUIRED_REFERRALS}</b> ta do'st\n"
        f"📨 Sizning referal havolangiz:\n<code>{ref_link}</code>"
    )

    kb = []
    if count >= REQUIRED_REFERRALS:
        kb.append([InlineKeyboardButton("🎁 Sovg'ani olish", callback_data="get_gift")])

    await query.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(kb) if kb else None
    )

# ─────────────────────────── callback: get_gift ─────────────────

async def get_gift_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if db.gift_received(user_id):
        await query.answer("⚠️ Siz allaqachon sovg'ani olib bo'lgansiz!", show_alert=True)
        return

    count = db.get_referral_count(user_id)
    if count < REQUIRED_REFERRALS:
        remaining = REQUIRED_REFERRALS - count
        await query.answer(f"Sizga yana {remaining} ta odam kerak!", show_alert=True)
        return

    try:
        invite = await context.bot.create_chat_invite_link(
            GIFT_CHANNEL_ID,
            member_limit=1,
            creates_join_request=False
        )
        db.mark_gift_received(user_id)
        await query.message.reply_text(
            f"🎊 <b>Tabriklaymiz!</b>\n\nMana sizning maxsus havolangiz:\n{invite.invite_link}",
            parse_mode="HTML"
        )
    except TelegramError as e:
        logger.error(f"Gift link error for {user_id}: {e}")
        await query.message.reply_text("❌ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")

# ─────────────────── join request handler ───────────────────────

async def join_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    if req.chat.id == CHANNEL_2_ID:
        user_id = req.from_user.id
        db.save_join_request(user_id)
        try:
            await context.bot.approve_chat_join_request(CHANNEL_2_ID, user_id)
        except TelegramError as e:
            logger.error(f"Could not approve join request for {user_id}: {e}")

# ─────────────────────────── admin ────────────────────────────

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    await update.message.reply_text(
        "🛠 <b>Admin Panel</b>\n\n"
        "/odam — Foydalanuvchilar soni\n"
        "/xabar &lt;matn&gt; — Hammaga xabar yuborish",
        parse_mode="HTML"
    )

async def odam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    count = db.get_total_users()
    await update.message.reply_text(
        f"👥 Botga /start bosgan foydalanuvchilar: <b>{count}</b> ta",
        parse_mode="HTML"
    )

async def xabar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not context.args:
        await update.message.reply_text("❗ Foydalanish: /xabar <matn>")
        return
    message_text = " ".join(context.args)
    users = db.get_all_user_ids()
    sent, failed = 0, 0
    for uid in users:
        try:
            await context.bot.send_message(uid, message_text)
            sent += 1
        except TelegramError:
            failed += 1
    await update.message.reply_text(
        f"✅ Yuborildi: <b>{sent}</b>\n❌ Muvaffaqiyatsiz: <b>{failed}</b>",
        parse_mode="HTML"
    )

# ─────────────────────────── main ───────────────────────────────

import asyncio

async def main():
    db.init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CommandHandler("odam", odam))
    app.add_handler(CommandHandler("xabar", xabar))
    app.add_handler(CallbackQueryHandler(check_sub_callback, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(get_gift_callback, pattern="^get_gift$"))
    app.add_handler(ChatJoinRequestHandler(join_request_handler))

    await app.initialize()
    await app.start()

    webhook_path = f"/webhook/{BOT_TOKEN}"
    full_webhook_url = f"{WEBHOOK_URL.rstrip('/')}{webhook_path}"

    await app.bot.set_webhook(full_webhook_url)

    # IMPORTANT: use run_polling OR external webhook server (Render + PTB limitation)
    await app.updater.start_polling()  # fallback stable mode

    await app.updater.idle()

if __name__ == "__main__":
    asyncio.run(main())

    await app.updater.idle()

if __name__ == "__main__":
    asyncio.run(main())

if __name__ == "__main__":
    main()
