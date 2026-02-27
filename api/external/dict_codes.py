import asyncio
from collections import defaultdict
from datetime import time


email_codes = defaultdict(dict)

async def set_email_code(user_id: int, code: str, ttl: int = 60):
    email_codes[user_id]['code'] = code
    email_codes[user_id]['expires'] = time.time() + ttl

async def get_email_code(user_id: int) -> tuple[str|None, bool]:
    if user_id not in email_codes:
        return None, False
    data = email_codes[user_id]
    if time.time() > data['expires']:
        del email_codes[user_id]
        return None, False
    return data['code'], True