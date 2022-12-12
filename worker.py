# from redis import Redis
import redis
from rq.job import Job
from rq import Queue
from rq.registry import FailedJobRegistry
import requests

# from quart import Quart

# app = Quart(__name__)

r = redis.Redis(decode_responses=True)

q = Queue(connection=r)
registry = FailedJobRegistry(queue=q)

def send_leaderboard_data(username, guesses, win):
    url = 'http://localhost:5500/leaderboard/post'
    response = requests.post(url, json={"uname":username, "guesses":guesses, "win":win})
    for job_id in registry.get_job_ids():
        job = Job.fetch(job_id, connection=r)
        print(job)

    # return response

