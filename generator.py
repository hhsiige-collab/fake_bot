from faker import Faker
import random
import json
from datetime import datetime, timedelta

fake = Faker('ru_RU')  # Русскоязычные данные

def generate_full_identity():
    # Базовая личность
    first_name = fake.first_name_male() if random.choice([True, False]) else fake.first_name_female()
    last_name = fake.last_name()
    patronymic = fake.middle_name_male() if first_name in fake.first_name_male() else fake.middle_name_female()
    
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=70)
    age = (datetime.now() - datetime.combine(birth_date, datetime.min.time())).days // 365
    
    # Адрес
    region = fake.region()
    city = fake.city()
    street = fake.street_name()
    house = random.randint(1, 150)
    apartment = random.randint(1, 200) if random.choice([True, False]) else None
    address = f"{city}, {street}, {house}"
    if apartment:
        address += f", кв. {apartment}"
    
    # Контакты
    phone = fake.phone_number()
    email = f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 99)}@{random.choice(['mail.ru', 'yandex.ru', 'gmail.com', 'bk.ru'])}"
    
    # Паспорт РФ (шаблон)
    passport_series = random.randint(1000, 9999)
    passport_number = random.randint(100000, 999999)
    passport_issued_by = fake.company()[:20] + " ОВД"
    passport_date = fake.date_between(start_date='-15y', end_date='-1y')
    
    # Банковская карта (тестовые номера, не настоящие)
    card_bins = {
        'Visa': '4',
        'MasterCard': '5',
        'Mir': '2200'
    }
    card_type = random.choice(list(card_bins.keys()))
    card_number = card_bins[card_type] + ''.join([str(random.randint(0,9)) for _ in range(15)])[:15]
    card_expiry = f"{random.randint(1,12):02d}/{random.randint(25,30)}"
    card_cvv = f"{random.randint(0,999):03d}"
    
    # СНИЛС
    snils = f"{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(100,999)} {random.randint(1,99):02d}"
    
    # ИНН
    inn = ''.join([str(random.randint(0,9)) for _ in range(12)])
    
    return {
        "ФИО": f"{last_name} {first_name} {patronymic}",
        "Пол": "Мужской" if first_name in fake.first_name_male() else "Женский",
        "Дата рождения": birth_date.strftime("%d.%m.%Y"),
        "Возраст": age,
        "Адрес": address,
        "Регион": region,
        "Телефон": phone,
        "Email": email,
        "Паспорт": f"{passport_series} {passport_number}",
        "Паспорт выдан": passport_issued_by,
        "Дата выдачи": passport_date.strftime("%d.%m.%Y"),
        "Карта": f"{card_type} {card_number}",
        "Срок карты": card_expiry,
        "CVV": card_cvv,
        "СНИЛС": snils,
        "ИНН": inn
    }

def generate_bulk(count: int):
    identities = []
    for _ in range(min(count, 50)):  # максимум 50 за раз
        identities.append(generate_full_identity())
    return identities

def format_identity(identity: dict) -> str:
    text = "🧾 **ФЕЙКОВАЯ ЛИЧНОСТЬ**\n\n"
    for key, value in identity.items():
        text += f"**{key}:** {value}\n"
    text += "\n_Данные сгенерированы автоматически. Карты тестовые, паспорт вымышленный._"
    return text