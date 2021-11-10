import asyncio
import websockets
from threading import Lock, Thread
from time import sleep
from queue import SimpleQueue

from binance import ThreadedWebsocketManager



class Job:
    create_key = object()

    job_instance = None

    @classmethod
    def get(cls):
        if(cls.job_instance is None):
            cls.job_instance = Job(cls.create_key)
        return cls.job_instance


    def __init__(self, create_key):
        assert(create_key == Job.create_key), \
            "Job objects must be created using Job.get()"

        # settings
        self.drop_ammount_to_notify_percent = 0.1
        self.trades_to_follow = 100
        self.symbol = "DOGEBTC"

        self.binance_manager = None
        self.job_running = False
        self.mutex = Lock()
        self.notifications = SimpleQueue()

        self.notifications_thread = None

        self.reset()


    def reset(self):
        self.prices = [0] * self.trades_to_follow
        self.current_price_index = 0
        self.max_price_index = 0


    def start(self):
        if self.job_running:
            return "Job is already running"
        
        if self.binance_manager == None:
            self.binance_manager = ThreadedWebsocketManager()
            self.binance_manager.start()

            self.notifications_thread = Thread(target=self.notifications_server)
            self.notifications_thread.start()

        self.job_running = True

        self.aggr_socket = self.binance_manager.start_aggtrade_socket(
            callback=self.request_handler,
            symbol=self.symbol
        )

        return "Job successfully started"


    def stop(self):
        if not self.job_running:
            return "Job is not running"

        self.job_running = False
        self.binance_manager.stop_socket(self.aggr_socket)
        
        self.reset()

        return "Job successfully stopped"


    def request_handler(self, info):
        with self.mutex:
            if 'p' not in info:
                return

            new_price = float(info['p'])

            if self.prices[self.max_price_index] > new_price * (1 + self.drop_ammount_to_notify_percent / 100):
                self.notifications.put(self.format_message(info['p']))

            self.prices[self.current_price_index] = new_price

            if self.max_price_index == self.current_price_index:
                # We have come full circle, update max price. Cycle backwards, so we have as much time until next update as possible
                for index in range(self.current_price_index - 1, -1, -1):
                    if self.prices[index] > self.prices[self.max_price_index]:
                        self.max_price_index = index
                        break
                if self.max_price_index == self.current_price_index:
                    for index in range(self.trades_to_follow - 1, self.current_price_index, -1):
                        if self.prices[index] > self.prices[self.max_price_index]:
                            self.max_price_index = index
                            break

            elif self.prices[self.current_price_index] >= self.prices[self.max_price_index]:
                self.max_price_index = self.current_price_index

            self.current_price_index += 1
            if self.current_price_index == self.trades_to_follow:
                self.current_price_index = 0



    def format_message(self, new_price):
        return {"max_price": str(self.prices[self.max_price_index]),
                "current_price": str(new_price)}


    def get_max_price(self):
        return self.prices[self.max_price_index]


    # Calculate min price here to not waste time checking every new price to get notifications faster.
    def get_min_price(self):
        with self.mutex:
            minPrice = self.prices[0]
            for price in self.prices:
                if price < minPrice:
                    if price == 0:
                        break
                    minPrice = price
            return minPrice


    def notifications_server(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self.notifications_server_loop())
        loop.close()


    async def notifications_server_loop(self):
        async with websockets.serve(self.client_callback, "localhost", 8765):
            await asyncio.Future()  # run forever

    async def client_callback(self, websocket, path):
        self.notifications = SimpleQueue()
        while True:
            message = self.notifications.get()
            await websocket.send(str(message))