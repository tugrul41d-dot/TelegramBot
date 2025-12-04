import sqlite3
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
import openai

# ===========================
# CONFIG (‼️ Kendin doldur)
# ===========================
TOKEN = "8356178245:AAFqnFMVAsKjHVGclkn13cpFPYZxld2bRXU"
openai.api_key = "OPENAI_API_ANAHTARIN"

ADMIN_ID = 123456789   # Admin Telegram ID

# ===========================
# LOGGING
# ===========================
logging.basicConfig(
    filename='bot.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ===========================
# VERITABANI
# ===========================
def db_connect():
    db = sqlite3.connect("bot.db")
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            firstname TEXT,
            is_admin INTEGER DEFAULT 0
        )
    """)
    db.commit()
    return db

db = db_connect()

def user_register(update: Update):
    user = update.effective_user
    db.execute(
        "INSERT OR IGNORE INTO users (id, username, firstname) VALUES (?, ?, ?)",
        (user.id, user.username, user.first_name)
    )
    db.commit()

# ===========================
# MENÜ BUTONLARI
# ===========================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🧠 Yapay Zekâ Sohbet", callback_data="ai_chat")],
        [InlineKeyboardButton("👤 Hesap Bilgileri", callback_data="profile")],
        [InlineKeyboardButton("🛠 Admin Paneli", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===========================
# /start KOMUTU
# ===========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_register(update)
    await update.message.reply_text(
        "Merhaba! ByteVectorBot'a hoş geldin 🤖",
        reply_markup=main_menu()
    )
    logging.info(f"Yeni kullanıcı: {update.effective_user.id}")

# ===========================
# CALLBACK HANDLER (MENÜ)
# ===========================
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "ai_chat":
        await query.edit_message_text("🧠 Bana bir şey yaz, yapay zekâ cevaplasın!")
        context.user_data["ai_mode"] = True

    elif query.data == "profile":
        info = db.execute("SELECT username, firstname FROM users WHERE id=?", (user_id,)).fetchone()
        await query.edit_message_text(
            f"👤 *Profil Bilgilerin*\n\n"
            f"• İsim: {info[1]}\n"
            f"• Kullanıcı adı: @{info[0]}",
            parse_mode="Markdown"
        )

    elif query.data == "admin_panel":
        if user_id != ADMIN_ID:
            await query.edit_message_text("❌ Bu bölüme erişim yok.")
            return

        await query.edit_message_text(
            "🛠 *Admin Paneli*\n\n"
            "/kullanicilar – Kayıtlı kullanıcıları göster",
            parse_mode="Markdown"
        )

# ===========================
# ADMIN KOMUTU
# ===========================
async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Yetkin yok.")
        return

    users = db.execute("SELECT id, username, firstname FROM users").fetchall()

    text = "📍 *Kayıtlı Kullanıcılar*\n\n"
    for u in users:
        text += f"• {u[2]} – @{u[1]} (ID: {u[0]})\n"

    await update.message.reply_text(text, parse_mode="Markdown")

# ===========================
# YAPAY ZEKA MESAJI
# ===========================
async def ai_response(msg: str):
    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": msg}]
    )
    return completion["choices"][0]["message"]["content"]

# ===========================
# MESAJ YAKALAYICI
# ===========================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_register(update)

    text = update.message.text

    # AI modu aktifse
    if context.user_data.get("ai_mode"):
        await update.message.reply_text("⏳ Düşünüyorum...")
        reply = await ai_response(text)
        await update.message.reply_text(reply)
        return

    # Normal cevap
    await update.message.reply_text(
        "📌 Menüden seçim yapabilirsiniz:",
        reply_markup=main_menu()
    )

# ===========================
# BOT ÇALIŞTIRMA
# ===========================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kullanicilar", admin_list))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
