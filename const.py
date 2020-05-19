import networkx as nx
import os

# Defining global variables

TOKEN_ADDRESS = "0x31aA9D3E2bd38d22CA3Ae9be7aae1D518fe46043"
SENDER_ADDRESS = "0x00D384EF74575E97884215e9f39142228c7ACfa8"
RECEIVER_1_ADDRESS = "0x002857f3a3BEa9DC0301D6DCf573692720f88B5a"
RECEIVER_2_ADDRESS = "0x0087b32F69DB0b92cA5F268b499017DC5ca6EBFA"
RECEIVER_3_ADDRESS = "0x00b349E94436A3873b0a8b76eCe15d5f131F3128"
RECEIVER_4_ADDRESS = "0x006daf7986d23b700A5361830B7961F45D252F8C"
RECEIVER_5_ADDRESS = "0x00a614cf3C67CF541c633728224Ca0d5EC82f1dE"
RECEIVER_6_ADDRESS = "0x00673b5556Db5Fe0DdDB0875bF565a3a4AE51Dcb"

RECEIVER_LIST = [
    RECEIVER_1_ADDRESS,
    RECEIVER_2_ADDRESS,
    RECEIVER_3_ADDRESS,
    RECEIVER_4_ADDRESS,
    RECEIVER_5_ADDRESS,
    RECEIVER_6_ADDRESS
]

KEYSTORE_PATH_RECEIVER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'receiver/key_storage/')
DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raiden_config.toml')
RAIDEN_NODE_TIMEOUT = 25 * 60
SHORTEST_PATHS = None
CODE_FILE_NAME = 'current_barcode.jpg'
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
BAR_CODE_FILE_PATH = os.path.abspath(CODE_FILE_NAME)


def create_token_network_topology():
    # This is hardcoded. To see the topology checkout Images/Network_topology.png
    g = nx.Graph()
    g.add_edge(SENDER_ADDRESS, RECEIVER_1_ADDRESS)
    g.add_edges_from([
        (RECEIVER_1_ADDRESS, RECEIVER_2_ADDRESS),
        (RECEIVER_1_ADDRESS, RECEIVER_4_ADDRESS),
        (RECEIVER_1_ADDRESS, RECEIVER_6_ADDRESS),
    ])
    g.add_edge(RECEIVER_2_ADDRESS, RECEIVER_3_ADDRESS)
    g.add_edge(RECEIVER_4_ADDRESS, RECEIVER_5_ADDRESS)

    """Belows code can be used to debug the Graph"""
    # plt.subplot(121)
    # nx.draw(G, with_labels=True, font_weight='bold')
    # plt.show()

    return g


NETWORK_GRAPH = create_token_network_topology()
