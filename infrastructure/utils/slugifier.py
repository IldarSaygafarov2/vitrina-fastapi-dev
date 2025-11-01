import slugify


def generate_slug(name: str) -> str:
    return slugify.slugify(name)
