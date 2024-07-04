import asyncio
import aiohttp
import random
import base64
import time

SEM_LIMIT = 150

def get_headers(token):
    return {
        'Authorization': f'Basic {token}'
    }

async def random_sleep():
    await asyncio.sleep(random.randrange(1, 6))

def generate_random_number(length=12):
    first_digit = random.randint(1, 9)
    remaining_digits = [random.randint(0, 9) for _ in range(length - 1)]
    random_number = str(first_digit) + ''.join(map(str, remaining_digits))
    return random_number

def import_credentials():
    with open("credentials.csv", "r") as file:
        phones = [row.strip().replace('"', '') for row in file.readlines()]
        credentials = [base64.b64encode(f"{row}:{row[-4:]}".encode()).decode() for row in phones]
    return credentials

async def get_new_blocks(session, headers, user_data: dict) -> dict:
    print("Getting new blocks")
    _url = f"http://192.168.167.110:8081/api/v1/getNewBlocks?lat={user_data['lat']}&lng={user_data['lng']}"
    async with session.get(_url, headers=headers) as response:
        response = await response.json()
        return response

async def get_main_categories(session, headers, user_data: dict) -> dict:
    print("Getting main categories")
    _url = f"http://192.168.167.110:8081/api/v1/main_categories?lang={user_data['lng']}"
    async with session.get(_url, headers=headers) as response:
        response = await response.json()
        return response

async def get_pages(session, headers, user_data: dict) -> dict:
    print("Getting pages")
    _url = f"http://192.168.167.110:8081/api/v1/pages?lang={user_data['lng']}"
    async with session.get(_url, headers=headers) as response:
        response = await response.json()
        return response

async def get_delivery_demand(session, headers, user_data: dict) -> dict:
    print("Getting delivery demand")
    _url = f"http://192.168.167.110:8081/api/v1/deliveryDemand?lang={user_data['lng']}"
    async with session.get(_url, headers=headers) as response:
        response = await response.json()
        return response

async def get_blocks(session, headers, user_data: dict) -> dict:
    print("Getting blocks")
    _url = f"http://192.168.167.110:8081/api/v1/getBlocks?lat={user_data['lat']}&lang={user_data['lng']}"
    async with session.get(_url, headers=headers) as response:
        response = await response.json()
        return response

async def enter_main_page(session, headers, user_data: dict) -> dict:
    _url = f"http://192.168.167.110:8081/api/v1/getManufacturers?lat={user_data['lat']}&lng={user_data['lng']}"
    print("Getting manufacturers", _url)
    await asyncio.gather(
        get_new_blocks(session, headers, user_data),
        get_main_categories(session, headers, user_data),
        get_pages(session, headers, user_data),
        get_delivery_demand(session, headers, user_data),
        get_blocks(session, headers, user_data)
    )
    async with session.get(_url, headers=headers) as response:
        response = await response.json()
        return response

async def get_manufacturer(session, headers, user_data: dict, manufacturer: dict):
    print(f"Getting manufacturer {manufacturer['url']} {manufacturer['id']}")
    _url = f"http://192.168.167.110:8081/api/v1/GetProductsWithCategory/{manufacturer['id']}"
    async with session.get(_url, headers=headers) as response:
        response = await response.json()
        return response

async def add_to_cart(session, headers, user_data: dict, product: dict):
    print("Adding to cart", headers)
    _url = f"http://192.168.167.110:8081/api/v1/addCart?lat={user_data['lat']}&lng={user_data['lng']}"
    data = {
        "id": product['id'],
        "qty": 2
    }
    async with session.post(_url, headers=headers, json=data) as response:
        return

async def remove_from_cart(session, headers, product: dict):
    print("Removing from cart")
    _url = f"http://192.168.167.110:8081/api/v1/removeProduct?id={product['id']}&lang=ru"
    async with session.get(_url, headers=headers) as response:
        response = await response.json()
        return response

async def get_cart(session, headers, user_data: dict):
    print("Getting cart")
    _url = f"http://192.168.167.110:8081/api/v1/getCart?lat={user_data['lat']}&lng={user_data['lng']}"
    async with session.get(_url, headers=headers) as response:
        print(await response.text())
        response = await response.json()
        return response

async def create_order(session, headers, user_data: dict, products: list, manufacturer: dict):
    print("Creating order")
    _url = "http://192.168.167.110:8081/api/v1/createOrder"
    data = {
        "is_click": 0,
        "dont_call": 0,
        "cupon_code": "",
        "cupon_sum": "",
        "cupon_type": "",
        "lat": f"{user_data['lat']}",
        "lng": f"{user_data['lng']}",
        "manufacturer_id": manufacturer['id'],
        "payment_id": 18,
        "pickup": 0,
        "products": products,
        "platform": 10
    }
    async with session.post(_url, headers=headers, json=data) as response:
        response = await response.json()
        print(response)
        return response

async def simulate_user(session, headers, sem, num: int, request_times: list):
    try:
        async with sem:
            user_data = {
                "num": num,
                "lat": f"41.31{generate_random_number()}",
                "lng": f"69.27{generate_random_number()}"
            }

            start_time = time.time()
            manufacturers = await enter_main_page(session, headers, user_data)
            elapsed_time = time.time() - start_time
            request_times.append(elapsed_time)

            if not manufacturers.get('data'):
                return
            active_manufacturers = list(filter(lambda x: x['is_active_now'] == 1 and x['is_pharmacy'] == 0, manufacturers['data']))

            products = await get_manufacturer(session, headers, user_data, active_manufacturers[0])
            if not products.get('data', {}).get('items'):
                return
            active_products = list(filter(lambda x: x['active'] == 1, products.get('data', {}).get('items')[0]['products']))
            if not active_products:
                return
            await random_sleep()

            # await add_to_cart(session, headers, user_data, active_products[0])
            cart = await remove_from_cart(session, headers, active_products[0])
            # await create_order(session, headers, user_data, cart)
            # await create_order(session, headers, user_data, active_products[:2], active_manufacturers[0])
    except Exception as e:
        print(f"Request #{num} failed: {e}")

async def main(credentials: list):
    sem = asyncio.Semaphore(SEM_LIMIT)
    headers = get_headers(credentials[random.randint(0, len(credentials) - 1)])
    request_times = []
    async with aiohttp.ClientSession() as session:
        tasks = [simulate_user(session, headers, sem, user_num, request_times) for user_num in range(5000)]
        await asyncio.gather(*tasks)

    if request_times:
        min_time = min(request_times)
        max_time = max(request_times)
        avg_time = sum(request_times) / len(request_times)
    else:
        min_time = max_time = avg_time = 0

    print(f"Min request time: {min_time} seconds")
    print(f"Max request time: {max_time} seconds")
    print(f"Average request time: {avg_time} seconds")

if __name__ == "__main__":
    start_time = time.time()
    credentials = import_credentials()
    asyncio.run(main(credentials))
    print(f"Total execution time: {time.time() - start_time} seconds")
