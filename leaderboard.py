from quart import Quart, request
from quart_schema import QuartSchema
import redis
import math
import json
import httpx
import socket
import os
import time
import asyncio

app = Quart(__name__)
QuartSchema(app)

r = redis.Redis(decode_responses=True)

domain = socket.getfqdn()
port = os.environ['PORT']
url = 'http://localhost:' + port + '/leaderboard/post'
print(url)

data={'url':url}

count = 1
loop = asyncio.get_event_loop()

async def retry():
    while True:
        try:
            response = httpx.post('http://mirdiland/client-register/',auth=('client','admin'), json=data)
            #print(response)
            response.raise_for_status()
            await asyncio.sleep(10)
        except httpx.HTTPStatusError as e:
            loop.call_later(100, retry)

def stop():
    task.cancel()

loop = asyncio.get_event_loop()
loop.call_later(10, stop)
task = loop.create_task(retry())

try:
    loop.run_until_complete(task)
except asyncio.CancelledError:
    pass

@app.route("/leaderboard/post", methods=["POST"])
async def postScore():

    user_details = await request.get_json()
    print(user_details)
    try:
        user_name = user_details["uname"]
        guesses = user_details["guesses"]
        win = user_details["win"]
    except TypeError:
        return {"msg":"Error: data improperly formed"}, 400

    game_score = win * (7 - guesses)

    # NOTE: INCRBY creates the key if it doesn't exist:
    # https://database.guide/redis-incrby-command-explained/
    t_score = r.hincrby(user_name, "total_score", game_score)
    t_games = r.hincrby(user_name, "no_of_games", 1)

    average = t_score / t_games
    r.zadd("leaderboard", {user_name: float(average)})
    return "success", 200



@app.route("/leaderboard", methods=["GET"])
async def get_leaderboard():
    """
    
    """
    top_users = r.zrevrange("leaderboard", 0, 9)

    return {"leaders":top_users}, 200
