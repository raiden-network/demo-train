import asyncio
import subprocess

from const import KEYSTOREPATHRECEIVER, PASSWORDFILE, ETH_RPC_ENDPOINT, MATRIX_SERVER


async def start_raiden_nodes(raiden_cls, receivers, delete_keystore=True, timeout=10):
    if delete_keystore:
        print("Removing old Raiden Databases")
        subprocess.run(
            "rm -fr ~/.raiden",
            shell=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL
        )

    raiden_nodes = {}

    for receiver_id, address in list(receivers.items()):
        raiden_node = raiden_cls(address=address,
                                 keystore_path=KEYSTOREPATHRECEIVER,
                                 password_file=PASSWORDFILE,
                                 eth_rpc_endpoint=ETH_RPC_ENDPOINT,
                                 api_endpoint="http://127.0.0.1:500{}".format(receiver_id),
                                 matrix_server=MATRIX_SERVER
        )
        raiden_nodes[address] = raiden_node
        raiden_node.start()

    done, pending = await asyncio.wait([asyncio.create_task(raiden_node.ensure_is_started())
                                        for raiden_node in raiden_nodes.values()], timeout=timeout)

    if len(pending) != 0:
        for task in pending:
            task.cancel()
        raise TimeoutError("It took more than {} minutes to start the Raiden Nodes".format(timeout))

    print("Raiden nodes are started")
    return raiden_nodes
