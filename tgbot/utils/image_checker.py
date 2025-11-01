import imagehash
from PIL import Image

from infrastructure.database.repo.requests import RequestsRepo


def is_image_same(image_1_path: str, image_2_path: str) -> bool:
    hash1 = imagehash.average_hash(Image.open(image_1_path))
    hash2 = imagehash.average_hash(Image.open(image_2_path))
    return hash1 == hash2


def get_image_hash_as_int(path: str):
    h = imagehash.average_hash(Image.open(path))
    return int(str(h), 16)


def get_image_hash_hex(path: str) -> str:
    return str(imagehash.average_hash(Image.open(path)))


def compare_hashes(hash1: str, hash2: str, max_distance: int = 5) -> bool:
    """
    Сравнивает два hex-хэша картинок.
    Возвращает True, если фото считаются одинаковыми (distance <= max_distance).
    """
    h1 = imagehash.hex_to_hash(hash1)
    h2 = imagehash.hex_to_hash(hash2)
    return (h1 - h2) <= max_distance


async def is_duplicate(new_image_path: str, repo: "RequestsRepo", max_distance: int = 5):
    new_hash = get_image_hash_hex(new_image_path)

    # берём все фото с их хэшами из базы
    db_images = await repo.advertisement_images.get_all_hashes()

    duplicates = []
    for img in db_images:
        if not img.image_hash:
            continue  # если ещё нет хэша

        if compare_hashes(new_hash, img.image_hash, max_distance):
            duplicates.append((img.id, img.advertisement_id))

    return duplicates