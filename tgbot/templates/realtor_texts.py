from infrastructure.database.models import User


def get_realtor_info(realtor: User):
    return f"""
Имя: {realtor.first_name}
Фамилия: {realtor.lastname}
Номер телефона: {realtor.phone_number}
Юзернейм: {realtor.tg_username}
"""
