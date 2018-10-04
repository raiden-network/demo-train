from quart import Quart, send_file, jsonify
from quart_cors import cors
import os

from utils import random_address, get_random_element

app = Quart(__name__)
app = cors(app)

NOF_ADDRESSES = 10

PROVIDER_MAP = {random_address(): 0 for _ in range(NOF_ADDRESSES)}


qrcode_file_path = os.path.abspath('current_qrcode.jpeg')

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


@app.route('/api/1/provider/qr/current')
async def get_current_qr_code():
    return send_file(qrcode_file_path)


