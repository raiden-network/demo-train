from collections.__init__ import defaultdict

from aiohttp import web


class FakeRaiden:

    def __init__(self, *, loop, address: str, port: int):
        self.loop = loop
        self.address = address
        self.port = port
        self.app = web.Application(loop=loop)
        self.app.router.add_routes(
            [web.get('/api/1/address', self.on_address),
             web.get('/api/1/payments/{token_address}/{partner_address}', self.on_payment_info)])
        self.handler = None
        self.server = None

        # mapping (token_address, partner_address) -> {nonce1: amount1, nonce2: amount2, ...}:
        self.payments = defaultdict(dict)

    async def start(self):
        port = self.port
        # FIXME make_handler() is deprecated, change to AppRunner API
        self.handler = self.app.make_handler()
        self.server = await self.loop.create_server(self.handler,
                                                    '127.0.0.1', port
                                                    )
        return {'localhost': port}

    async def stop(self):
        self.server.close()
        await self.server.wait_closed()
        await self.app.shutdown()
        await self.handler.shutdown()
        await self.app.cleanup()

    def make_payment(self, token_address, partner_address, nonce, amount):
        # TODO checkme
        self.payments[(token_address, partner_address)][nonce] = amount

    async def on_address(self, request):
        return web.json_response(encode_address(self.address))

    # TODO cache the list of events eventually
    async def on_payment_info(self, request):
        token_address = request.match_info['token_address']
        partner_address = request.match_info['partner_address']
        payments = self.payments.get((token_address, partner_address))
        events = []
        if payments is not None:
            for nonce, amount in payments.items():
                events.append(
                    encode_payment_received_success_event(nonce, amount)
                )

        return web.json_response(events)


def encode_payment_received_success_event(identifier: int, amount: int) -> dict:
    return {"event": "EventPaymentReceivedSuccess", "amount": amount, "identifier": identifier}


def encode_address(address) -> dict:
    return {"our_address": address}