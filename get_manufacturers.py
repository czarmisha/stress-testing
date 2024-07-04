import asyncio
import time
import aiohttp
import random

url = "https://api.bringo.uz/api/v1/getManufacturers?lat=41.32658270002777&lng=69.31340320000001"

headers = {
    'Authorization': 'Basic OTk4OTczMzM0NjgyOjQ2ODI=',
    'Cookie': 'PHPSESSID=t9hf5fual6r2gakksfb4lo1b0l'
}

def generate_random_number(length=14):
    # Первую цифру генерируем отдельно, чтобы избежать ведущего нуля
    first_digit = random.randint(1, 9)
    # Оставшиеся цифры генерируем в диапазоне от 0 до 9
    remaining_digits = [random.randint(0, 9) for _ in range(length - 1)]
    # Собираем все вместе и преобразуем в строку
    random_number = str(first_digit) + ''.join(map(str, remaining_digits))
    return random_number

async def fetch():
    start = time.time()
    _url = f"https://api.bringo.uz/api/v1/getManufacturers?lat=41.{generate_random_number()}&lng=69.{generate_random_number()}"
    print(f"Requesting {_url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response =  await response.text()
            print(f"Time: {time.time() - start}")
            return response

async def main():
    
    tasks = [fetch() for _ in range(500)]
    await asyncio.gather(*tasks)
    # responses = await asyncio.gather(*tasks)
    # for response in responses:
    #     print(response)

# Запуск основной асинхронной функции
asyncio.run(main())
