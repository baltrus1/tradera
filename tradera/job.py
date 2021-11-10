from threading import Lock
from time import sleep

from binance import ThreadedWebsocketManager

import logging
from binance.lib.utils import config_logging
from queue import Queue


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
        self.tradesToFollow = 100
        self.symbol = "DOGEBTC"

        self.binance_manager = ThreadedWebsocketManager()
        self.binance_manager.start()
        self.job_running = False
        self.mutex = Lock()

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
            callback=self.notify,
            symbol=self.symbol
        )

        return "Job successfully started"


    def stop(self):
        if not self.job_running:
            return "Job is not running"

        self.binance_manager.stop_socket(self.aggr_socket)
        self.job_running = False
        self.reset()

        return "Job successfully stopped"


    def notify(self, info):
        print(info)
        with self.mutex:
            if 'p' not in info:
                return

            newPrice = float(info['p'])

            if self.prices[self.maxPriceIndex] > newPrice * (1 + self.drop_ammount_to_notify_percent / 100):
                print("Price has decrease by quite a lot:")
                print("Max price in the last 100 trades: " + "{:.8f}".format(self.prices[self.maxPriceIndex]))
                print("Current price: " + "{:.8f}".format(newPrice))

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












