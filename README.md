# Tradera
A simple notification server that follows last aggregated trades in binance and notifies any connected client about price drop with a certain precision.

Install missing dependencies: 'django', 'asyncio', 'websockets' with 'python3 -m pip install <>'

# Usage

Run server: 
python3 manage.py runserver

Start following trades: 
python3 job_manager.py start

Stop following trades: 
python3 job_manager.py stop

Get highest and lowest prices in the last trades that job follows:
python3 ./job_manager.py prices

Run an example notification client service that just logs notifications from server:
python3 notificaton_logger.py

# Testing

install pytest:
python3 -m pip install pytest

While in root directory run:
python3 -m pytest
