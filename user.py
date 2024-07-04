import asyncio
import time
import aiohttp
from random import randrange

url = "http://192.168.167.110:8081/api/v1/user/change/profile"

headers = {
    'Authorization': 'Basic OTk4OTczMzM0NjgyOjQ2ODI=',
    'Cookie': 'PHPSESSID=t9hf5fual6r2gakksfb4lo1b0l'
}

success = 0
failed = 0
request_times = []

semaphore = asyncio.Semaphore(5000)

async def fetch(num: int, session: aiohttp.ClientSession):
    async with semaphore:
        global success
        global failed
        start = time.time()
        print(f"Requesting {url}, #{num}")
        rnd = randrange(1000)
        data = {
            "full_name": f"test{rnd}",
            "email": "test@mail.com"
        }
        try:
            async with session.post(url, headers=headers, json=data) as response:
                response_text = await response.text()
                elapsed_time = time.time() - start
                request_times.append(elapsed_time)
                print(f"Time: {elapsed_time}, #{num}")
                if response.status == 200:
                    success += 1
                else:
                    failed += 1
                print(response_text)
                return response_text
        except Exception as e:
            failed += 1
            print(f"Request #{num} failed: {e}")

async def main():
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(i, session) for i in range(100000)]
        await asyncio.gather(*tasks)
    end_time = time.time()
    total_time = end_time - start_time

    if request_times:
        min_time = min(request_times)
        max_time = max(request_times)
        avg_time = sum(request_times) / len(request_times)
    else:
        min_time = max_time = avg_time = 0

    print(f"Total time: {total_time} seconds")
    print(f"Min request time: {min_time} seconds")
    print(f"Max request time: {max_time} seconds")
    print(f"Average request time: {avg_time} seconds")

try:
    asyncio.run(main())
except Exception as e:
    print(e)

print(f"Success: {success}")
print(f"Failed: {failed}")
