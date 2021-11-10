#!/usr/bin/env python

import requests
from sys import argv
from time import sleep

base_url = "http://localhost:8000/"

suffix = "prices"
if len(argv) == 2:
	suffix = argv[1]

r = requests.get(url = base_url + suffix)

try:
    data = r.json()
    print("Max price: {:.8f}".format(float(data["max"])))
    print("Min price: {:.8f}".format(float(data["min"])))
except ValueError as e:
	print(r.text)

