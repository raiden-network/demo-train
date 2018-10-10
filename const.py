import json
import networkx
import networkx as nx
import os

# Defining global variables
from eth_utils import to_checksum_address

TOKEN_ADDRESS = "0xC1bF364ed86E2a8cd9766FCDa51a53ef3c5fFCb8"
SENDER_ADDRESS = "0x00D384EF74575E97884215e9f39142228c7ACfa8"
RECEIVER_1_ADDRESS = "0x002857f3a3BEa9DC0301D6DCf573692720f88B5a"
RECEIVER_2_ADDRESS = "0x0087b32F69DB0b92cA5F268b499017DC5ca6EBFA"
RECEIVER_3_ADDRESS = "0x00b349E94436A3873b0a8b76eCe15d5f131F3128"
RECEIVER_4_ADDRESS = "0x0006CaA8eE29a6bbe66b74bf77b30371816AFD7c"
RECEIVER_5_ADDRESS = "0x006daf7986d23b700A5361830B7961F45D252F8C"
RECEIVER_6_ADDRESS = "0x00a614cf3C67CF541c633728224Ca0d5EC82f1dE"
RECEIVER_7_ADDRESS = "0x00C68910D9C719a5612790343862bcdF49d6a29A"
RECEIVER_8_ADDRESS = "0x00673b5556Db5Fe0DdDB0875bF565a3a4AE51Dcb"

KEYSTOREPATHRECEIVER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'receiver/key_storage/')
ETH_RPC_ENDPOINT = "http://geth.ropsten.ethnodes.brainbot.com:8545"
PASSWORDFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'wallet_password.txt')

MATRIX_SERVER = "https://transport02.raiden.network"

RAIDEN_NODE_TIMEOUT = 15*60


def get_receiver_addresses():
    """"Puts all addresses in our KeyStorePath in a dict with key 'receiver_id' """
    KeyStorePath = KEYSTOREPATHRECEIVER
    addresses = {}

    for i, f in enumerate(os.listdir(KeyStorePath)):
        fullpath = os.path.join(KeyStorePath, f)
        if os.path.isfile(fullpath):
            try:
                with open(fullpath) as data_file:
                    data = json.load(data_file)
                    addresses[i + 1] = to_checksum_address(str(data['address']))

            except (
                    IOError,
                    json.JSONDecodeError,
                    KeyError,
                    OSError,
                    UnicodeDecodeError,
            ) as ex:
                # Invalid file - skip
                if f.startswith('UTC--'):
                    # Should be a valid account file - warn user
                    msg = 'Invalid account file'
                    if isinstance(ex, IOError) or isinstance(ex, OSError):
                        msg = 'Can not read account file (errno=%s)' % ex.errno
                    if isinstance(ex, json.decoder.JSONDecodeError):
                        msg = 'The account file is not valid JSON format'
    print("Addresses are %s" % addresses)
    return addresses


SHORTEST_PATHS = None
CODE_FILE_NAME = 'current_barcode'
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
BAR_CODE_FILE_PATH = os.path.abspath(CODE_FILE_NAME)


def create_token_network_topology():
    # This is hardcoded. To see the topology checkout Images/Network_topology.png
    g = nx.Graph()
    g.add_edge(SENDER_ADDRESS, RECEIVER_1_ADDRESS)
    g.add_edges_from([
        (RECEIVER_1_ADDRESS, RECEIVER_2_ADDRESS),
        (RECEIVER_1_ADDRESS, RECEIVER_5_ADDRESS),
        (RECEIVER_1_ADDRESS, RECEIVER_8_ADDRESS)
    ])
    g.add_edge(RECEIVER_2_ADDRESS, RECEIVER_3_ADDRESS)
    g.add_edge(RECEIVER_3_ADDRESS, RECEIVER_4_ADDRESS)
    g.add_edge(RECEIVER_5_ADDRESS, RECEIVER_6_ADDRESS)
    g.add_edge(RECEIVER_6_ADDRESS, RECEIVER_7_ADDRESS)

    """Belows code can be used to debug the Graph"""
    # plt.subplot(121)
    # nx.draw(G, with_labels=True, font_weight='bold')
    # plt.show()

    return g