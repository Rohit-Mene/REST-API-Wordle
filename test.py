from quart import Quart, request
from quart_schema import QuartSchema
import redis
import math
import json
import httpx
import socket
import os

domain = socket.getfqdn()
port = os.environ
#url = domain + port + '/leaderboard/'
print(domain)