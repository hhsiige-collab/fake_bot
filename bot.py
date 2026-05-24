import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8721625713:AAGCqILZTihaYaokmWkYiu5-mRgUN4tvN2Q"

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает!")

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Генерация пока отключена для теста")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen))
    
    port = int(os.environ.get("PORT", 8080))
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    
    print(f"Порт: {port}, URL: {webhook_url}")
    app.run_webhook(listen="0.0.0.0", port=port, webhook_url=webhook_url)

if __name__ == "__main__":
    main()
