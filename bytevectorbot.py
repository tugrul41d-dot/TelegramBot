import logging
import asyncio
import nest_asyncio
from pytz import timezone
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from dotenv import load_dotenv
import os

# Ortam değişkenlerini yükle
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Event loop düzeltmesi
nest_asyncio.apply()

# Logging ayarları
logging.basicConfig(
    filename='C:\\@ByteVectorBot\\bot.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Merhaba Tugrul! Ben ByteVectorBot 🤖")
    logging.info(f"{update.effective_user.username} komutu kullandı: /start")

# /yardim komutu ve butonlar
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📄 Hakkında", callback_data='hakkinda')],
        [InlineKeyboardButton("📬 İletişim", callback_data='iletisim')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📌 Ne yapmak istersiniz?", reply_markup=reply_markup)
    logging.info(f"{update.effective_user.username} komutu kullandı: /yardim")

# Callback buton handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'hakkinda':
        await query.edit_message_text("Ben Tugrul tarafından geliştirilen bir Telegram botuyum. Görevim: işleri kolaylaştırmak 🤖")
    elif query.data == 'iletisim':
        await query.edit_message_text("Geliştirici: Tugrul\nİletişim: tugrul@example.com")
    logging.info(f"{query.from_user.username} butona tıkladı: {query.data}")

# Akıllı mesaj yanıtlayıcı
async def mesaj_yanitla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mesaj = update.message.text.lower()
    kullanici = update.effective_user.first_name or "kullanıcı"

    if "merhaba" in mesaj:
        yanit = f"Merhaba {kullanici}! Nasılsın? 😊"
    elif "teşekkür" in mesaj:
        yanit = "Rica ederim, her zaman buradayım! 🤖"
    elif "ne işe yararsın" in mesaj or "ne yaparsın" in mesaj:
        yanit = "Ben bir Telegram botuyum. Komutlarla veya mesajlarla sana yardımcı olabilirim!"
    else:
        yanit = "Bu konuda emin değilim 🤔 Ama /yardim yazarak neler yapabileceğimi görebilirsin."

    await update.message.reply_text(yanit)
    logging.info(f"{kullanici} mesaj gönderdi: {mesaj}")

# Ana fonksiyon
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("yardim", help_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_yanitla))

    logging.info("Bot başlatıldı")
    await app.run_polling()

# Giriş noktası
if __name__ == "__main__":
    asyncio.run(main())
