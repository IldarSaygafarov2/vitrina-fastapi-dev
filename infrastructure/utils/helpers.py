import random


def generate_code():
    return str(random.randint(100000, 999999))


async def get_unique_code(repo):
    unique_codes = await repo.advertisements.get_all_unique_ids()
    while True:
        code = generate_code()

        if code not in unique_codes:
            return code
