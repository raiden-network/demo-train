#!/bin/bash

# rm -fr ~/.raiden

cd /tmp

exec ~/.virtualenvs/raiden/bin/python -m raiden --keystore-path  ~/demo-train/sender/key_storage --eth-rpc-endpoint http://parity.kovan.ethnodes.brainbot.com:8545 --environment-type development --accept-disclaimer --address 0x00D384EF74575E97884215e9f39142228c7ACfa8 --network-id 42 --password-file ~/demo-train/wallet_password.txt --log-config=raiden:ERROR --disable-debug-logfile
