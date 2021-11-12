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

            new_price = info['p']
            self.post_notification(new_price)

            self.prices[self.current_price_index] = float(new_price)

            self.update_max_price()

            self.current_price_index += 1
            if self.current_price_index == self.trades_to_follow:
                self.current_price_index = 0


    def post_notification(self, price_str):
        if self.prices[self.max_price_index] > float(price_str) * (1 + self.drop_ammount_to_notify_percent / 100):
            self.notifications.put(self.format_message(price_str))


    def format_message(self, new_price):
        return {"decreased_price": str(new_price)}

    def update_max_price(self):
        if self.max_price_index == self.current_price_index:
            # We have come full circle without finding bigger price than the one in current index.
            # Since current is deleted, cycle through to find a new one. Doing it backwards to give as much time as possible until next update
            # Search backwards from current index to 0
            for index in range(self.current_price_index - 1, -1, -1):
                if self.prices[index] > self.prices[self.max_price_index]:
                    self.max_price_index = index

            # Search backwards from end to current index
            for index in range(self.trades_to_follow - 1, self.current_price_index, -1):
                if self.prices[index] > self.prices[self.max_price_index]:
                    self.max_price_index = index

        elif self.prices[self.current_price_index] >= self.prices[self.max_price_index]:
            self.max_price_index = self.current_price_index

    def get_max_price(self):
        return self.prices[self.max_price_index]


    # Assume we want to optimize for notifications and this is only used sometimes when /prices gets requested - 
    # no reason to try to update min price every time new price event arrives
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
            try:
                await websocket.send(str(message))
            except:
                break