# Tradera
A server with background job that follows last aggregated trades in binance and notifies connected client about price drop with a certain precision

Settings could be adjusted in job.py constructor for now

# Installation
Recommended setting up in virtual environment

From project root:

	pip3 install -r requirements.txt 

# Usage

Run server: 

	./manage.py runserver

### Server's endpoints

* /start - starts the job

* /stop - stops the job

* /prices - returns lowest and highest prices among the ones job is following

### Helpers
Helper to access endpoints:
	
	./job_manager.py <option:[start/stop/prices]>

Run an example notification client service that just logs notifications from server (job has to be started):
	
	./notificaton_logger.py

# Testing
From root directory run:
	
	python3 -m pytest
