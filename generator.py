from faker import Faker
import random
from datetime import datetime

fake = Faker('ru_RU')

def generate_full_identity():
    gender = random.choice(['male', 'female'])
    first_name = fake.first_name_male() if gender == 'male' else fake.first_name_female()
    last_name = fake.last_name()
    patronymic = fake.middle_name_male() if gender == 'male' else fake.middle_name_female()
    
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=70)
    age = (datetime.now() - datetime.combine(birth_date, datetime.min.time())).days // 365
    
    region = fake.region()
    city = fake.city()
    street = fake.street_name()
    house = random.randint(1, 150)
    apartment = random.randint(1, 200) if random.choice([True, False]) else None
    address = f"{city}, {street}, {house}"
    if apartment:
        address += f", кв. {apartment}"
    
    phone = fake.phone_number()
    email = f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 99)}@{random.choice(['mail.ru', 'yandex.ru', 'gmail.com', 'bk.ru'])}"
    
    passport_series = random.randint(1000, 9999)
    passport_number = random.randint(100000, 999999)
    passport_issued_by = fake.company()[:20] + " ОВД"
    passport_date = fake.date_between(start_date='-15y', end_date='-1y')
    
    card_type = random.choice(['Visa', 'MasterCard', 'Mir'])
    if card_type == 'Visa':
        card_prefix = '4'
    elif card_type == 'MasterCard':
        card_prefix = '5'
    else:
        card_prefix = '2200'
    card_number = card_prefix + ''.join([str(random.randint(0,9)) for _ in range(15 - len(card_prefix))])
    card_expiry = f"{random.randint(1,12):02d}/{random.randint(25,30)}"
    card_cvv = f"{random.randint(0,999):03d}"
    
    snils = f"{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(100,999)} {random.randint(1,99):02d}"
    inn = ''.join([str(random.randint(0,9)) for _ in range(12)])
    
    return {
        "ФИО": f"{last_name} {first_name} {patronymic}",
        "Пол": "Мужской" if gender == 'male' else "Женский",
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

def format_identity(identity: dict) -> str:
    text = "🧾 **СГЕНЕРИРОВАННАЯ ЛИЧНОСТЬ**\n\n"
    for key, value in identity.items():
        text += f"**{key}:** {value}\n"
    text += "\n_Данные вымышленные, созданы автоматически._"
    return text
