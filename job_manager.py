#!/usr/bin/env python

import requests
from sys import argv, exit
from time import sleep

base_url = "http://localhost:8000/"

options = ["start", "stop", "prices"]
if len(argv) != 2 or argv[1] not in options:
    print("Usage: ./job_manager.py <options:[start/stop/prices]>")
    exit(0)

suffix = argv[1]
r = requests.get(url = base_url + suffix)

try:
    data = r.json()
    print("Max price: {:.8f}".format(float(data["max"])))
    print("Min price: {:.8f}".format(float(data["min"])))
except ValueError as e:
	print(r.text)

