import os

import bcrypt


def generate_unique_key():
    key = os.urandom(16)
    hashed_key = bcrypt.hashpw(key, bcrypt.gensalt()).decode('utf-8')
    return key.hex(), hashed_key
