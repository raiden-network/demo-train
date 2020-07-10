import logging
import os

from app import TrainApp
import code128

from quart import Quart, jsonify, send_file, safe_join
from quart_cors import cors
from const import (
    CODE_FILE_NAME,
    DEFAULT_CONFIG_FILE,
    SCRIPT_PATH,
    SENDER_ADDRESS,
    NETWORK_GRAPH,
)
from deployment import get_receiver_addresses
from network import NetworkTopology

LOGGER_FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=LOGGER_FORMAT, datefmt='[%H:%M:%S]')
log = logging.getLogger()
log.setLevel(logging.INFO)

app = Quart(__name__)
app = cors(app)

train_app = None
network = NetworkTopology(NETWORK_GRAPH, SENDER_ADDRESS, get_receiver_addresses())
current_provider = None


def on_new_bar_code(bar_code, file_path):
    factor = 4
    bar_code = bar_code.resize((int(bar_code.width * factor), int(bar_code.height * factor)))
    bar_code.save(str(file_path))


def barcode_factory(address, nonce):
    return code128.image("(" + str(address) + "," + str(nonce) + ")")


def build_app(mock='', config_file=DEFAULT_CONFIG_FILE):
    global train_app
    mock_arduino = False
    mock_raiden = False

    mocked_modules = set(mock.split(' '))

    if 'raiden' in mocked_modules:
        mock_raiden = True
    if 'arduino' in mocked_modules:
        mock_arduino = True

    if config_file:
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file)

    train_app = TrainApp.build_app(network, mock_arduino, mock_raiden, config_file)

    return app


@app.before_serving
async def start_services():
    train_app.start()
    log.debug('Initialization completed')


@app.after_serving
async def end_services():
    train_app.stop()


@app.route('/api/v1/_debug')
async def get_debug_info():
    return train_app._track_loop


@app.route('/api/v1/provider/current')
async def get_current_provider():
    data = {
        "address": train_app.current_provider_address,
        "identifier": train_app.current_nonce
    }
    return jsonify(data)


@app.route('/api/v1/provider/qr/current')
def get_current_qr_code():
    return send_file(safe_join(SCRIPT_PATH, CODE_FILE_NAME))


@app.route('/api/v1/path/current')
async def get_current_path():
    return jsonify(network.shortest_path_from_sender(train_app.current_provider_address))


# TODO register logging output as exception handler for tasks
def custom_exception_handler(loop, context):
    # first, handle with default handler
    loop.default_exception_handler(context)

    exception = context.get('exception')
    if isinstance(exception, Exception):
        log.info(context)
        loop.stop()
