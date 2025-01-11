import os
import bcrypt


def generate_unique_key():
    key = os.urandom(16)
    hashed_key = bcrypt.hashpw(key, bcrypt.gensalt()).decode('utf-8')
    return key.hex(), hashed_key

def verify_key(user_input, hashed_key):
    return bcrypt.checkpw(bytes.fromhex(user_input), hashed_key.encode('utf-8'))
