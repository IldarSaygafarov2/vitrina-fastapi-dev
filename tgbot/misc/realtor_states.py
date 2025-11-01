from aiogram.fsm.state import State, StatesGroup


class RealtorCreationState(StatesGroup):
    first_name = State()
    lastname = State()
    phone_number = State()
    tg_username = State()
    photo = State()


class RealtorUpdatingState(StatesGroup):
    first_name = State()
    lastname = State()
    phone_number = State()
    tg_username = State()
    photo = State()
