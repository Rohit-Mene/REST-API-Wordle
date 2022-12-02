from quart import Quart, request
from quart_schema import QuartSchema
import redis
import math
import json

app = Quart(__name__)
QuartSchema(app)

r = redis.Redis()

@app.route("/postScore/", methods=["POST"])
async def postScore():

    userDetails = await request.get_json()
    game_id = userDetails.get('post_score').get('game_id')
    no_of_guesses = userDetails.get('post_score').get('no_of_guesses')
    game_status = userDetails.get('post_score').get('game_status')

    
    guess_to_score = {1:6,2:5,3:4,4:3,5:2,6:1}
    

    if game_status == "win":
        current_score = guess_to_score.get(no_of_guesses)
    else:
        current_score = 0      
    
    score=current_score
    games= 1
    if r.hexists(game_id,"total_score"):

        score = r.hincrby(game_id,"total_score", current_score)
        games = r.hincrby(game_id,"no_of_games", 1)
        
    else:
    
        result = r.hmset(game_id,{   
        "no_of_games": 1,
        "total_score":current_score
})
    average = math.ceil(score/games)
    r.zadd("leaderBoard",{average:game_id})
    rank = r.zrange("leaderBoard",0,2) 
    res = []
    for l in rank:
        res.append(l.decode('utf-8'))
    return json.dumps(res)


@app.route("/leaderboard", methods=["GET"])
async def get_leaderboard():
    """
    
    """
    top_users = r.zrevrange("leaderBoard", 0, 9)
    print('hrm')
    print(top_users)

    return None
