from quart import Quart, request
from quart_schema import QuartSchema
import redis
import math
import json

app = Quart(__name__)
QuartSchema(app)

r = redis.Redis(decode_responses=True)

@app.route("/leaderboard/post", methods=["POST"])
async def postScore():

    user_details = await request.get_json()
    print(user_details)
    try:
        user_name = user_details["uname"]
        guesses = user_details["guesses"]
        win = user_details["win"]
    except TypeError:
        return {msg:"Error: data improperly formed"}, 400

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
