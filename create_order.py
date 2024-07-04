import asyncio
import time
import aiohttp

url = "http://192.168.167.110:8081/api/v1/createOrder?delivery_type=1"

headers = {
    'Authorization': 'Basic OTk4OTczMzM0NjgyOjQ2ODI=',
    'Cookie': 'PHPSESSID=t9hf5fual6r2gakksfb4lo1b0l'
}

success = 0

async def fetch(num: int):
    start = time.time()
    print(f"Requesting {url}, #{num}")
    data = {
        "is_click": 0,
        "dont_call": 0,
        "cupon_code": "",
        "cupon_sum": "",
        "cupon_type": "",
        "lat": "41.30998151759552",
        "lng": "69.24311024242839",
        "manufacturer_id": 991,
        "payment_id": 18,
        "pickup": 0,
        "products": [
            {
                "id": 90426,
                "count": 1
            }
        ],
        "platform": 10
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            response =  await response.text()
            print(f"Time: {time.time() - start}, #{num}")
            global success
            success += 1
            print(response)
            return response

async def main():
    
    tasks = [fetch(i) for i in range(1)]
    await asyncio.gather(*tasks)
try:
    asyncio.run(main())
except Exception as e:
    print(e)

print(success)
