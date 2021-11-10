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


    def notifications_server(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self.notifications_server_loop())
        loop.close()


    def __init__(self, create_key):
        assert(create_key == Job.create_key), \
            "Job objects must be created using Job.get()"

        # settings
        self.drop_ammount_to_notify_percent = 0.1
        self.tradesToFollow = 100
        self.symbol = "DOGEBTC"

        self.binance_manager = ThreadedWebsocketManager()
        self.binance_manager.start()
        self.job_running = False
        self.mutex = Lock()
        self.notifications = SimpleQueue()

        self.notifications_thread = Thread(target=self.notifications_server)
        self.notifications_thread.start()

        self.reset()


    def reset(self):
        self.prices = [0] * self.tradesToFollow
        self.currentPriceIndex = 0
        self.maxPriceIndex = 0
        self.minPriceIndex = 0


    def start(self):
        if self.job_running:
            return "Job is already running"
        
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

            newPrice = float(info['p'])

            if self.prices[self.maxPriceIndex] > newPrice * (1 + self.drop_ammount_to_notify_percent / 100):
                self.notifications.put(self.format_message(newPrice))
                
            self.prices[self.currentPriceIndex] = newPrice

            if self.maxPriceIndex == self.currentPriceIndex:
                # We have come full circle, update max price. Cycle backwards, so we have as much time until next update as possible
                for index in range(self.currentPriceIndex - 1, -1, -1):
                    if self.prices[index] > self.prices[self.maxPriceIndex]:
                        self.maxPriceIndex = index
                        break
                if self.maxPriceIndex == self.currentPriceIndex:
                    for index in range(self.tradesToFollow - 1, self.currentPriceIndex, -1):
                        if self.prices[index] > self.prices[self.maxPriceIndex]:
                            self.maxPriceIndex = index
                            break

            elif self.prices[self.currentPriceIndex] >= self.prices[self.maxPriceIndex]:
                self.maxPriceIndex = self.currentPriceIndex

            self.currentPriceIndex += 1
            if self.currentPriceIndex == self.tradesToFollow:
                self.currentPriceIndex = 0



    def format_message(self, newPrice):
        return "Price has dropped:\n\t" +                      \
        "Max price: " +                                      \
        "{:.8f}".format(self.prices[self.maxPriceIndex]) + \
        ", Current price: " +                                \
        "{:.8f}".format(newPrice)                          \


    def getMaxPrice(self):
        return self.prices[self.maxPriceIndex]


    # Calculate min price here to not waste time checking every new price to get notifications faster.
    def getMinPrice(self):
        with self.mutex:
            minPrice = self.prices[0]
            for price in self.prices:
                if price < minPrice:
                    if price == 0:
                        break
                    minPrice = price
            return minPrice

    async def notifications_server_loop(self):
        async with websockets.serve(self.client_callback, "localhost", 8765):
            await asyncio.Future()  # run forever

    async def client_callback(self, websocket, path):
        while True:
            message = self.notifications.get()
            await websocket.send(str(message))