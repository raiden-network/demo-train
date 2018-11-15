import asyncio
import json
import os
import subprocess
import logging
from time import sleep

from eth_utils import to_checksum_address

from const import RAIDEN_NODE_TIMEOUT, KEYSTORE_PATH_RECEIVER

log = logging.getLogger()


async def start_raiden_nodes(raiden_cls, receivers, delete_keystore=False, timeout=RAIDEN_NODE_TIMEOUT,
                             config_file=None):
    # TODO define the datadir separately to avoid deleting all raiden data!
    # TODO find a possibility to persist blockchain data for faster startup
    if delete_keystore:
        log.debug("Removing old Raiden Databases")
        subprocess.run(
            "rm -fr ~/.raiden",
            shell=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL
        )

    raiden_nodes = {}

    for receiver_id, address in list(receivers.items()):
        raiden_node = raiden_cls(address=address, api_endpoint="http://127.0.0.1:500{}".format(receiver_id),
                                 config_file=config_file)
        raiden_nodes[address] = raiden_node
        raiden_node.start()
        # Added a little sleep to avoid a race for debug files
        # This throws an error which is handled by raiden but it's still better to avoid it
        sleep(15)

    done, pending = await asyncio.wait([asyncio.create_task(raiden_node.ensure_is_started())
                                        for raiden_node in raiden_nodes.values()], timeout=timeout)

    if len(pending) != 0:
        for task in pending:
            task.cancel()
        raise TimeoutError("It took more than {} minutes to start the Raiden Nodes"
                           .format(timeout / 60)
                           )

    log.info("All Raiden nodes are started")
    return raiden_nodes


# TODO refactor/ determine if needed
def get_receiver_addresses():
    """"Puts all addresses in our KeyStorePath in a dict with key 'receiver_id' """
    keystore_path = KEYSTORE_PATH_RECEIVER
    addresses = {}

    for i, f in enumerate(os.listdir(keystore_path)):
        fullpath = os.path.join(keystore_path, f)
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
    return addresses
