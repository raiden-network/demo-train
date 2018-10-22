import networkx as nx

from const import TOKEN_ADDRESS


class NetworkTopology:

    def __init__(self, graph, sender_address, receiver_addresses, token_address=TOKEN_ADDRESS):
        self._graph = graph
        self._shortes_paths = nx.single_source_shortest_path(graph, sender_address)
        self.sender_address = sender_address
        self.receivers = receiver_addresses
        self.token_address = token_address

    def shortest_path_from_sender(self, to_address):
            return self._shortes_paths[to_address]
