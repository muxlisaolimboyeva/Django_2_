import random
import string


def generate_promo_code():
    letters = string.ascii_uppercase
    numbers = string.digits
    return ''.join(random.choices(letters + numbers, k=8))
