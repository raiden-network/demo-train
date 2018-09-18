import os

# Defining global variables
TOKEN_ADDRESS = "0xC1bF364ed86E2a8cd9766FCDa51a53ef3c5fFCb8"
SENDER_ADDRESS = "0x00D384EF74575E97884215e9f39142228c7ACfa8"

KEYSTOREPATHRECEIVER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'receiver/key_storage/')
ETH_RPC_ENDPOINT = "http://geth.ropsten.ethnodes.brainbot.com:8545"
PASSWORDFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'wallet_password.txt')
