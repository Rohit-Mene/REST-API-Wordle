# from redis import Redis
import redis
from rq.job import Job
from rq import Queue
from rq.registry import FailedJobRegistry
# import requests
import httpx

from quart import Quart

app = Quart(__name__)

r = redis.Redis(decode_responses=True)

q = Queue(connection=r)
registry = FailedJobRegistry(queue=q)

def send_leaderboard_data(username, guesses, win):

    data = {'username': username, 'guesses': guesses, 'win':win}
    url = 'http://localhost:5500/leaderboard/post'
    holder = httpx.post(url, json=data)
    app.logger.info(holder)
    # for job_id in registry.get_job_ids():
    #     job = Job.fetch(job_id, connection=r)

    # return response

