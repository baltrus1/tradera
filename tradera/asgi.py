"""
ASGI config for tradera project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from tradera.websocket import websocket_applciation

django_application = get_asgi_application()

async def application(scope, receive, send):
	if scope['type'] == 'http':
		print("got http request")
		await django_application(scope, receive, send)
	elif scope['type'] == 'websocket':
		print("got ws request")
		await websocket_applciation(scope, receive, send)
	else:
		raise NotImplementedError(f"Unknown scope type {scope['type']}")
