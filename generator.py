from faker import Faker
import random
import json
from datetime import datetime
import requests
import hashlib
import qrcode
from io import BytesIO
import zipfile
import os

# Хранилище для настроек пользователей (в реальном боте лучше использовать БД)
user_settings = {}

def get_faker(locale='ru_RU'):
    locales = {
        'ru': 'ru_RU',
        'us': 'en_US',
        'de': 'de_DE',
        'cn': 'zh_CN'
    }
    return Faker(locales.get(locale, 'ru_RU'))

def luhn_checksum(card_number):
    """Проверка контрольной суммы карты по алгоритму Луна"""
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10

def generate_valid_card(card_type='Visa'):
    """Генерация валидного номера карты"""
    bins = {
        'Visa': '4',
        'MasterCard': '5',
        'Mir': '2200'
    }
    prefix = bins.get(card_type, '4')
    # Генерируем 15 цифр, последняя будет контрольной
    partial = prefix + ''.join([str(random.randint(0,9)) for _ in range(15 - len(prefix))])
    for check_digit in range(10):
        if luhn_checksum(partial + str(check_digit)) == 0:
            return partial + str(check_digit)
    return partial + '0'

def generate_full_identity(locale='ru', include_fields=None):
    """Генерация полной личности с выбором полей"""
    fake = get_faker(locale)
    
    # Если не указаны поля, включаем все
    if include_fields is None:
        include_fields = ['fio', 'gender', 'birth', 'address', 'region', 'phone', 'email', 'passport', 'card', 'snils', 'inn']
    
    identity = {}
    
    # ФИО и пол
    if 'fio' in include_fields or 'gender' in include_fields:
        gender = random.choice(['male', 'female'])
        first_name = fake.first_name_male() if gender == 'male' else fake.first_name_female()
        last_name = fake.last_name()
        patronymic = fake.middle_name_male() if gender == 'male' else fake.middle_name_female()
        
        if 'fio' in include_fields:
            identity["ФИО"] = f"{last_name} {first_name} {patronymic}"
        if 'gender' in include_fields:
            identity["Пол"] = "Мужской" if gender == 'male' else "Женский"
    
    # Дата рождения и возраст
    if 'birth' in include_fields:
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=70)
        age = (datetime.now() - datetime.combine(birth_date, datetime.min.time())).days // 365
        identity["Дата рождения"] = birth_date.strftime("%d.%m.%Y")
        identity["Возраст"] = age
    
    # Адрес
    if 'address' in include_fields:
        region = fake.region() if locale == 'ru' else fake.state()
        city = fake.city()
        street = fake.street_name()
        house = random.randint(1, 150)
        apartment = random.randint(1, 200) if random.choice([True, False]) else None
        address = f"{city}, {street}, {house}"
        if apartment:
            address += f", кв. {apartment}"
        identity["Адрес"] = address
        identity["Регион"] = region
    
    # Контакты
    if 'phone' in include_fields:
        identity["Телефон"] = fake.phone_number()
    if 'email' in include_fields:
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(10,99)}@{random.choice(['mail.ru', 'yandex.ru', 'gmail.com', 'bk.ru'])}"
        identity["Email"] = email
    
    # Паспорт
    if 'passport' in include_fields:
        passport_series = random.randint(1000, 9999)
        passport_number = random.randint(100000, 999999)
        passport_issued_by = fake.company()[:20] + " ОВД"
        passport_date = fake.date_between(start_date='-15y', end_date='-1y')
        identity["Паспорт"] = f"{passport_series} {passport_number}"
        identity["Паспорт выдан"] = passport_issued_by
        identity["Дата выдачи"] = passport_date.strftime("%d.%m.%Y")
    
    # Банковская карта
    if 'card' in include_fields:
        card_type = random.choice(['Visa', 'MasterCard', 'Mir'])
        card_number = generate_valid_card(card_type)
        card_expiry = f"{random.randint(1,12):02d}/{random.randint(25,30)}"
        card_cvv = f"{random.randint(0,999):03d}"
        identity["Карта"] = f"{card_type} {card_number}"
        identity["Срок карты"] = card_expiry
        identity["CVV"] = card_cvv
    
    # СНИЛС
    if 'snils' in include_fields:
        snils = f"{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(100,999)} {random.randint(1,99):02d}"
        identity["СНИЛС"] = snils
    
    # ИНН
    if 'inn' in include_fields:
        inn = ''.join([str(random.randint(0,9)) for _ in range(12)])
        identity["ИНН"] = inn
    
    return identity

def generate_face_photo():
    """Генерация фото лица через thispersondoesnotexist.com"""
    try:
        response = requests.get('https://thispersondoesnotexist.com/', timeout=10)
        if response.status_code == 200:
            return BytesIO(response.content)
    except:
        pass
    return None

def generate_qr(data: str):
    """Генерация QR-кода с данными"""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def generate_zip(identities, format_type='txt'):
    """Создание ZIP-архива с личностями"""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, identity in enumerate(identities):
            if format_type == 'json':
                content = json.dumps(identity, ensure_ascii=False, indent=2)
                filename = f"person_{i+1}.json"
            else:
                content = "\n".join([f"{k}: {v}" for k, v in identity.items()])
                filename = f"person_{i+1}.txt"
            zip_file.writestr(filename, content)
    zip_buffer.seek(0)
    return zip_buffer

def format_identity(identity: dict, include_qr=False) -> tuple:
    """Форматирование личности с возможностью генерации QR"""
    text = "🧾 **ФЕЙКОВАЯ ЛИЧНОСТЬ**\n\n"
    for key, value in identity.items():
        text += f"**{key}:** {value}\n"
    text += "\n_Данные сгенерированы автоматически._"
    
    qr_bytes = None
    if include_qr:
        qr_data = "\n".join([f"{k}: {v}" for k, v in identity.items()])
        qr_bytes = generate_qr(qr_data)
    
    return text, qr_bytes

def generate_bulk(locale='ru', count=10, include_fields=None):
    """Массовая генерация"""
    identities = []
    for _ in range(min(count, 500)):  # макс 500
        identities.append(generate_full_identity(locale, include_fields))
    return identities
