# Tradera
A simple notification server that follows last aggregated trades in binance and notifies any connected client about price drop with a certain precision.

Install missing dependencies: django, asyncio, websockets etc with 'pip3 install <>'

# Usage
# Run server
./manage.py runserver

### Start following trades
./job_manager.py start

### Stop following trades
./job_manager.py stop

### Get highest and lowest prices in the last trades that job follows
./job_manager.py prices

### Run an example notification client service that just logs notifications from server
./notificaton_logger.py
