from quart import Quart, request
from quart_schema import QuartSchema
import redis

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

    if r.hexists(game_id,no_of_guesses):

        r.hincrby(game_id,"total_score", current_score)
        r.hincrby(game_id,"no_of_games", 1)
    else:
    
        result = r.hmset(game_id,{   
        "no_of_games": no_of_guesses,
        "total_score":guess_to_score   
})

    

    





# result = r.hset(1, "name", "jane")

# print(result)

# result = r.hexists(1)
# print(result) 

# resultget = r.hget(1, "name")
# print(resultget)




# result = r.hmset("leader",{
# "game_id": 1,
# "no_of_games": 1,
# "total_score":1
# })


# result1 = r.hmset("leader",{
# "game_id": 2,
# "no_of_games": 2,
# "total_score":2
# })



# print(r.hmget("leader","game_id","no_of_games"))


# result = r.hexists("person1-hash","money")
# print(result)
# r.hset("person1-hash", "money", 100)

# # Hash increment by
# result = r.hincrby("person1-hash", "money", 10)
# print(result)

# result2 = r.hincrby("person1-hash", "money", -20)
# print(result2)