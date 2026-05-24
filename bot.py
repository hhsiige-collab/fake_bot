import logging
import os
import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import config
from generator import (
    generate_full_identity, format_identity, generate_face_photo,
    generate_bulk, generate_zip, user_settings, get_faker
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Клавиатуры
def get_main_keyboard():
    return ReplyKeyboardMarkup([
        ['/gen', '/gen_passport', '/gen_card'],
        ['/gen_snils', '/gen_face', '/gen_100'],
        ['/settings', '/country', '/help']
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎭 **Фейкогенератор — ПОЛНАЯ ВЕРСИЯ**\n\n"
        "Команды:\n"
        "/gen — полная личность\n"
        "/gen_passport — только паспортные данные\n"
        "/gen_card — только банковская карта\n"
        "/gen_snils — СНИЛС + ИНН\n"
        "/gen_face — сгенерировать фото лица\n"
        "/gen 50 — массовая генерация (2-500)\n"
        "/country — выбрать страну (RU/US/DE/CN)\n"
        "/settings — настроить поля вывода\n"
        "/qr — показать QR-код последней личности\n"
        "/save_txt — сохранить в TXT\n"
        "/save_json — сохранить в JSON\n\n"
        "_Бот умеет валидировать номера карт и генерировать QR-коды_",
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔧 **Команды подробно:**\n\n"
        "/gen [число] — генерация (1-500 личностей). Пример: /gen 25\n"
        "/gen_passport — только паспорт\n"
        "/gen_card — только карта (с проверкой Луна)\n"
        "/gen_snils — СНИЛС + ИНН\n"
        "/gen_face — нейросетевое фото лица\n"
        "/country — сменить страну (Россия/США/Германия/Китай)\n"
        "/settings — выбрать, какие поля показывать\n"
        "/qr — QR-код с данными последней личности\n"
        "/save_txt — выгрузить в TXT файл\n"
        "/save_json — выгрузить в JSON файл",
        parse_mode='Markdown'
    )

async def gen_one(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    locale = user_settings.get(user_id, {}).get('locale', 'ru')
    fields = user_settings.get(user_id, {}).get('fields', None)
    
    await update.message.reply_text("⏳ Генерирую...")
    identity = generate_full_identity(locale, fields)
    text, qr_bytes = format_identity(identity, include_qr=False)
    
    # Сохраняем последнюю личность для QR и экспорта
    context.user_data['last_identity'] = identity
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def gen_with_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    locale = user_settings.get(user_id, {}).get('locale', 'ru')
    fields = user_settings.get(user_id, {}).get('fields', None)
    
    if not context.args:
        await gen_one(update, context)
        return
    
    try:
        count = int(context.args[0])
        if count < 1 or count > 500:
            await update.message.reply_text("Число от 1 до 500.")
            return
    except:
        await update.message.reply_text("Введи число. Пример: /gen 50")
        return
    
    await update.message.reply_text(f"⏳ Генерирую {count} личностей...")
    identities = generate_bulk(locale, count, fields)
    
    if count == 1:
        identity = identities[0]
        text, _ = format_identity(identity)
        context.user_data['last_identity'] = identity
        await update.message.reply_text(text, parse_mode='Markdown')
    else:
        # Отправляем ZIP-архив
        zip_buffer = generate_zip(identities, 'txt')
        await update.message.reply_document(
            document=zip_buffer,
            filename=f"identities_{count}.zip",
            caption=f"📦 {count} личностей в TXT"
        )

async def gen_passport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    locale = user_settings.get(user_id, {}).get('locale', 'ru')
    fields = ['fio', 'gender', 'birth', 'passport']
    identity = generate_full_identity(locale, fields)
    text, _ = format_identity(identity)
    context.user_data['last_identity'] = identity
    await update.message.reply_text(text, parse_mode='Markdown')

async def gen_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    locale = user_settings.get(user_id, {}).get('locale', 'ru')
    fields = ['card']
    identity = generate_full_identity(locale, fields)
    text, _ = format_identity(identity)
    context.user_data['last_identity'] = identity
    await update.message.reply_text(text, parse_mode='Markdown')

async def gen_snils(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    locale = user_settings.get(user_id, {}).get('locale', 'ru')
    fields = ['snils', 'inn']
    identity = generate_full_identity(locale, fields)
    text, _ = format_identity(identity)
    context.user_data['last_identity'] = identity
    await update.message.reply_text(text, parse_mode='Markdown')

async def gen_face(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎨 Генерирую фото лица через нейросеть...")
    photo_bytes = generate_face_photo()
    if photo_bytes:
        await update.message.reply_photo(photo=photo_bytes, caption="🎭 Сгенерированное лицо (thispersondoesnotexist.com)")
    else:
        await update.message.reply_text("❌ Не удалось сгенерировать фото. Попробуй позже.")

async def gen_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    identity = context.user_data.get('last_identity')
    if not identity:
        await update.message.reply_text("Сначала сгенерируй личность командой /gen")
        return
    
    qr_bytes = format_identity(identity, include_qr=True)[1]
    if qr_bytes:
        await update.message.reply_photo(photo=qr_bytes, caption="📱 QR-код с данными личности")

async def save_txt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    identity = context.user_data.get('last_identity')
    if not identity:
        await update.message.reply_text("Нет сохранённой личности. Сначала сделай /gen")
        return
    
    content = "\n".join([f"{k}: {v}" for k, v in identity.items()])
    await update.message.reply_document(
        document=BytesIO(content.encode('utf-8')),
        filename="person.txt",
        caption="📄 Личность в TXT"
    )

async def save_json(update: Update, context: ContextTypes.DEFAULT_TYPE):
    identity = context.user_data.get('last_identity')
    if not identity:
        await update.message.reply_text("Нет сохранённой личности. Сначала сделай /gen")
        return
    
    content = json.dumps(identity, ensure_ascii=False, indent=2)
    await update.message.reply_document(
        document=BytesIO(content.encode('utf-8')),
        filename="person.json",
        caption="📄 Личность в JSON"
    )

async def country_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup([
        ['🇷🇺 Россия', '🇺🇸 США'],
        ['🇩🇪 Германия', '🇨🇳 Китай'],
        ['🔙 Назад']
    ], resize_keyboard=True)
    await update.message.reply_text("Выбери страну:", reply_markup=keyboard)

async def set_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if 'Россия' in text:
        locale = 'ru'
        country_name = 'Россия'
    elif 'США' in text:
        locale = 'us'
        country_name = 'США'
    elif 'Германия' in text:
        locale = 'de'
        country_name = 'Германия'
    elif 'Китай' in text:
        locale = 'cn'
        country_name = 'Китай'
    else:
        await update.message.reply_text("Возврат в главное меню", reply_markup=get_main_keyboard())
        return
    
    if user_id not in user_settings:
        user_settings[user_id] = {}
    user_settings[user_id]['locale'] = locale
    
    await update.message.reply_text(f"✅ Страна изменена на {country_name}", reply_markup=get_main_keyboard())

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup([
        ['✅ Все поля', '📛 Только ФИО+дата'],
        ['💳 Только карта+паспорт', '📞 Только контакты'],
        ['🔙 Назад']
    ], resize_keyboard=True)
    await update.message.reply_text("Настройка полей вывода:", reply_markup=keyboard)

async def set_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if 'Все поля' in text:
        fields = None
        msg = "Будут показываться все поля"
    elif 'Только ФИО+дата' in text:
        fields = ['fio', 'gender', 'birth']
        msg = "Только ФИО, пол, дата рождения"
    elif 'Только карта+паспорт' in text:
        fields = ['passport', 'card']
        msg = "Только паспорт и банковская карта"
    elif 'Только контакты' in text:
        fields = ['phone', 'email']
        msg = "Только телефон и email"
    else:
        await update.message.reply_text("Возврат в главное меню", reply_markup=get_main_keyboard())
        return
    
    if user_id not in user_settings:
        user_settings[user_id] = {}
    user_settings[user_id]['fields'] = fields
    
    await update.message.reply_text(f"✅ {msg}", reply_markup=get_main_keyboard())

async def handle_menu_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Главное меню", reply_markup=get_main_keyboard())

def main():
    from io import BytesIO
    from telegram.ext import CallbackContext
    
    app = Application.builder().token(config.BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("gen", gen_with_count))
    app.add_handler(CommandHandler("gen_passport", gen_passport))
    app.add_handler(CommandHandler("gen_card", gen_card))
    app.add_handler(CommandHandler("gen_snils", gen_snils))
    app.add_handler(CommandHandler("gen_face", gen_face))
    app.add_handler(CommandHandler("qr", gen_qr))
    app.add_handler(CommandHandler("save_txt", save_txt))
    app.add_handler(CommandHandler("save_json", save_json))
    app.add_handler(CommandHandler("country", country_menu))
    app.add_handler(CommandHandler("settings", settings_menu))
    
    # Обработчики кнопок
    app.add_handler(MessageHandler(filters.Regex('^(🇷🇺 Россия|🇺🇸 США|🇩🇪 Германия|🇨🇳 Китай)$'), set_country))
    app.add_handler(MessageHandler(filters.Regex('^(✅ Все поля|📛 Только ФИО\+дата|💳 Только карта\+паспорт|📞 Только контакты)$'), set_settings))
    app.add_handler(MessageHandler(filters.Regex('^🔙 Назад$'), handle_menu_back))
    
    print("🤖 Фейкогенератор (полная версия) запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
