import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import config
from generator import generate_full_identity, format_identity

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎭 **Бот-генератор фейков**\n\n/gen — создать личность",
        parse_mode='Markdown'
    )

async def gen_one(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Генерирую...")
    identity = generate_full_identity()
    await update.message.reply_text(format_identity(identity), parse_mode='Markdown')

def main():
    app = Application.builder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen_one))
    
    port = int(os.environ.get("PORT", 8080))
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    
    print(f"Запуск на порту {port}, вебхук: {webhook_url}")
    app.run_webhook(listen="0.0.0.0", port=port, webhook_url=webhook_url)

if __name__ == "__main__":
    main()
