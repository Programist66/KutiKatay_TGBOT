import os
import bcrypt
import random

def generate_random_thai_string(length=100):
    thai_characters = (
        'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง',
        'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ', 'ฎ',
        'ฏ', 'ถ', 'ท', 'ธรรม', 'ณ', 'ด', 'ต',
        'ถ', 'ท', 'ธ', 'น', 'บ', 'ป', 'ผ',
        'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร',
        'ล', 'ว', 'ศ', 'ษ', 'ส', 'ห', 'ฬ',
        'อ', 'ฮ'
    )
    return ''.join(random.choices(thai_characters, k=length))


def generate_unique_key():
    thai_key = generate_random_thai_string(100)
    return thai_key