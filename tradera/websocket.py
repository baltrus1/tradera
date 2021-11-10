from time import sleep
from .job import Job
import asyncio
async def websocket_applciation(scope, receive, send):
    while True:
        event = await receive()

        if event['type'] == 'websocket.connect':
            await send({
                'type': 'websocket.accept'
            })
            break
        
        if event['type'] == 'websocket.disconnect':
            break
        
        message = Job.get().anyData()
        await send({
                    'type': 'websocket.send',
                    'text': message
                })
