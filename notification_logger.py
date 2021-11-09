#!/usr/bin/env python

"""Helper that automatically starts the job, runs for a 
minute or until stopped and logs notification."""

import requests
from sys import argv
from time import sleep

base_url = "http://127.0.0.1:8000/"

suffix = "prices"
if len(argv) == 2:
	suffix = argv[1]

r = requests.get(url = base_url + suffix)

print(r.text)

