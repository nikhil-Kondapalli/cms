import re


def generate_slug(text: str) -> str:
    return re.sub(r"[\W_]+", "-", text.lower()).strip("-")
