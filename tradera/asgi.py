"""
ASGI config for tradera project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

django_application = get_asgi_application()

async def application(scope, receive, send):
	if scope['type'] == 'http':
		await django_application(scope, receive, send)
	else:
		raise NotImplementedError(f"Unknown scope type {scope['type']}")
