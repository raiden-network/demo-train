from quart import Quart
from quart import jsonify

from utils import random_address, get_random_element

app = Quart(__name__)

NOF_ADDRESSES = 10

PROVIDER_MAP = {random_address(): 0 for _ in range(NOF_ADDRESSES)}


@app.route('/api/1/provider/current')
async def get_current_provider():
    global PROVIDER_MAP

    address, counter = get_random_element(PROVIDER_MAP)
    data = {
        "address": address,
        "identifier": counter
    }
    PROVIDER_MAP[address] += 1
    return jsonify(data)


