import asyncio
import random
from eth_utils import encode_hex


def random_address():
    return encode_hex((random.getrandbits(20 * 8)).to_bytes(20, 'big'))


def get_random_element(_dict: dict):
    random_key = random.choice(list(_dict.keys()))
    return random_key, _dict[random_key]


async def wait_for_event(event):
    await event.wait()


async def context_switch():
    await asyncio.sleep(0.001)