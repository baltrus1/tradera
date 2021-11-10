#!/usr/bin/env python

import asyncio
import websockets
from time import sleep

async def receiver():
	async with websockets.connect("ws://localhost:8765") as websocket:
		while True:
			data = await websocket.recv()
			print("Got notification! Data: " + str(data))
asyncio.run(receiver())
