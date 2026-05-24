import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import config
from generator import generate_full_identity, format_identity
import requests
from io import BytesIO

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# КНОПКИ НА РУССКОМ
main_keyboard = ReplyKeyboardMarkup([
    ['👤 Генерация личности', '🎭 Генерация лица'],
    ['📄 Генерация паспорта', '💳 Генерация карты'],
    ['📞 Генерация контактов', '📦 Массовая генерация']
], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎭 **Фейкогенератор**\n\n"
        "👇 Нажми на кнопку, чтобы сгенерировать:\n\n"
        "• 👤 Генерация личности — все данные разом\n"
        "• 🎭 Генерация лица — фото через нейросеть\n"
        "• 📄 Генерация паспорта — только паспортные данные\n"
        "• 💳 Генерация карты — только банковская карта\n"
        "• 📞 Генерация контактов — телефон и email\n"
        "• 📦 Массовая генерация — сразу 5 личностей",
        parse_mode='Markdown',
        reply_markup=main_keyboard
    )

async def gen_identity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Генерирую личность...")
    identity = generate_full_identity()
    await update.message.reply_text(format_identity(identity), parse_mode='Markdown')

async def gen_face(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎨 Генерирую лицо через нейросеть... Подожди 5-10 секунд.")
    try:
        response = requests.get('https://thispersondoesnotexist.com/', timeout=15)
        if response.status_code == 200:
            photo_bytes = BytesIO(response.content)
            await update.message.reply_photo(photo=photo_bytes, caption="🎭 Сгенерированное лицо (AI)")
        else:
            await update.message.reply_text("❌ Ошибка генерации. Попробуй позже.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: не удалось загрузить фото. Попробуй ещё раз.")

async def gen_passport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Генерирую паспортные данные...")
    identity = generate_full_identity()
    text = f"📄 **ПАСПОРТНЫЕ ДАННЫЕ**\n\n**ФИО:** {identity.get('ФИО', '—')}\n**Дата рождения:** {identity.get('Дата рождения', '—')}\n**Паспорт:** {identity.get('Паспорт', '—')}\n**Кем выдан:** {identity.get('Паспорт выдан', '—')}\n**Дата выдачи:** {identity.get('Дата выдачи', '—')}"
    await update.message.reply_text(text, parse_mode='Markdown')

async def gen_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Генерирую банковскую карту...")
    identity = generate_full_identity()
    text = f"💳 **БАНКОВСКАЯ КАРТА**\n\n{identity.get('Карта', '—')}\n**Срок:** {identity.get('Срок карты', '—')}\n**CVV:** {identity.get('CVV', '—')}"
    await update.message.reply_text(text, parse_mode='Markdown')

async def gen_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Генерирую контакты...")
    identity = generate_full_identity()
    text = f"📞 **КОНТАКТЫ**\n\n**Телефон:** {identity.get('Телефон', '—')}\n**Email:** {identity.get('Email', '—')}"
    await update.message.reply_text(text, parse_mode='Markdown')

async def gen_mass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Генерирую 5 личностей...")
    for i in range(5):
        identity = generate_full_identity()
        await update.message.reply_text(f"**#{i+1}**\n\n{format_identity(identity)}", parse_mode='Markdown')

# ОБРАБОТЧИК КНОПОК
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '👤 Генерация личности':
        await gen_identity(update, context)
    elif text == '🎭 Генерация лица':
        await gen_face(update, context)
    elif text == '📄 Генерация паспорта':
        await gen_passport(update, context)
    elif text == '💳 Генерация карты':
        await gen_card(update, context)
    elif text == '📞 Генерация контактов':
        await gen_contacts(update, context)
    elif text == '📦 Массовая генерация':
        await gen_mass(update, context)
    else:
        await update.message.reply_text("Используй кнопки 👇", reply_markup=main_keyboard)

def main():
    app = Application.builder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    
    print("🤖 Бот с кнопками и генерацией лиц запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
