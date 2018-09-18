#!/bin/bash

rm -fr ~/.raiden

exec ~/.virtualenvs/raiden/bin/python -m raiden --keystore-path  ~/keys/ --eth-rpc-endpoint http://geth.ropsten.ethnodes.brainbot.com:8545 --no-web-ui --accept-disclaimer --address 0x00F3fF781d1eCf923aFa54611CE6C3c9E679D1E3 --password-file ~/demo/StartServiceRaiden/password.txt --disable-debug-logfile

