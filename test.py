import asyncio
import sys
from postgre.database import check_connection

if __name__ == "__main__":
    # Фикс для Windows, чтобы работал драйвер psycopg3
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    # Запускаем проверку
    asyncio.run(check_connection())