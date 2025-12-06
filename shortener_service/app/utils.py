import string, random

def generate_short_code(length: int = 7):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))