import collections
import dataclasses
from http.client import HTTPResponse, responses
import json
import random
from re import S
import sqlite3
from wsgiref import headers
from quart import Quart,g,request,abort,Response
import databases

from quart_schema import QuartSchema,RequestSchemaValidationError,validate_request
app = Quart(__name__)
QuartSchema(app)


async def _get_db():
    db = getattr(g, "_sqlite_db", None)
    if db is None:
        db = g._sqlite_db = databases.Database('sqlite+aiosqlite:project1')
        await db.connect()
    return db


@app.teardown_appcontext
async def close_connection(exception):
    db = getattr(g, "_sqlite_db", None)
    if db is not None:
         await db.disconnect()



@app.route("/greet",methods=["GET"])
async def return_Hello():
    db = await _get_db()
    all_data = await db.fetch_all("select * from USERDATA")

    return list(map(dict,all_data))

@app.route("/registeruser/",methods=["POST"])
async def registerUser():
    db = await _get_db()
    data = await request.form
    dat_tup={'name':data['name'],'password':data['pass']}

    try:
     await db.execute("""INSERT INTO USERDATA(user_name,user_pass) VALUES(:name,:password)""",dat_tup,)
    except sqlite3.IntegrityError as e:
     abort(409,e)

    return Response("User Registration Successful!",status=201)

@app.route("/login/",methods=["GET"])
async def loginUser():
    db = await _get_db()
    data =  request.authorization
    if data:
     try:
      userDet = await db.fetch_one("select * from USERDATA where user_name = :user and user_pass= :pass",values={"user": data['username'], "pass": data['password']})
      if userDet is None: 
         return Response("Unsuccessful authentication",status=401,headers=dict({'WWW-Authenticate': 'Basic realm="Access to staging site"'}))
     except sqlite3.IntegrityError as e:
        abort(409,e)
     return Response(json.dumps({"authenticated":True,"user ID": userDet[2]}),status=200)
    else:
        return Response("Invalid Request!", status=400)
    

@dataclasses.dataclass
class Guess:
    game_id: int
    guess: str

@app.route("/guess/", methods=["POST"])
#@validate_request(Guess)
async def make_guess():
    db = await _get_db()
    data = await request.form
    guess_made={'game_id':data['game_id']}
    file = open('valid.json')
    word_list = json.load(file)
    #obtain secret word
    try:
        secret_word = await db.fetch_val(
            """
            SELECT secret_word FROM USERGAMEDATA WHERE game_id = :game_id
            """,
            guess_made,
        )
        #test if guess is correct
        if data['guess'] == secret_word:
            try:
                #if correct word decrease guess remaining and change game state to false
                await db.execute(
                    """ 
                        UPDATE USERGAMEDATA SET guess_cnt = guess_cnt - 1, game_sts = FALSE WHERE game_id = :game_id;
                    """,
                    guess_made
                )
            except sqlite3.IntegrityError as e:
                abort(500, e)
            #if correct return 
            return Response(json.dumps({"Correct word"}),status=200)
        #if guess is not correct but valid 
        elif data['guess'] in word_list:
            try:
                #decrease guesses remaining
                await db.execute(
                    """ 
                        UPDATE USERGAMEDATA SET guess_cnt = guess_cnt - 1 WHERE game_id = :game_id;
                    """,
                    guess_made
                )
            except sqlite3.IntegrityError as e:
                abort(500, e)
            #obtain new guess count to return
            try:
                guess_rem = await db.fetch_val(
                    """
                        SELECT guess_cnt FROM USERGAMEDATA WHERE game_id = :game_id;
                    """,
                    guess_made
                )
            except sqlite3.IntegrityError as e:
                abort(500, e)
            guess_word = str(data['guess'])
            #new lists to store letter positions
            correct_spot_list = []
            correct_letter_list = []
            #nested for loops to find letters that are correct but not in correct place
            for index2 in range(len(guess_word)):
                for index3 in range(len(secret_word)):
                    if secret_word[index3] == guess_word[index2] and index2 == index3:
                        correct_spot_list.append(index2)
                    elif secret_word[index3] == guess_word[index2] and index2 != index3:
                        correct_letter_list.append(index2)
            if len(correct_spot_list) > 0:
                for i in range(len(correct_letter_list)):
                    for j in range(len(correct_spot_list)):
                        if correct_letter_list[i] == correct_spot_list[j]:
                            correct_letter_list.remove(correct_spot_list[j])
            letter = [*set(correct_letter_list)]
            spot = [*set(correct_spot_list)]           
            #nested for loop to remove duplicate values from the two lists
            spot_to_string = ' '.join(map(str,spot))
            letter_to_string = ' '.join(map(str,letter))
            return Response(json.dumps('{valid :TRUE ,  guess_remaining :' + str(guess_rem) + ', correct position :' + spot_to_string + ', correct letter incorrect spot :' + letter_to_string + '}'),status=200)
        #if guess is not on valid list tell the user to try a different word
        else:
            return Response(json.dumps({"invalid guess, try again"}),status=200) 
        
    except sqlite3.IntegrityError as e:
        abort(409, e)


@app.route("/games/<int:user_id>", methods=["GET"])
async def all_games(user_id):
    db = await _get_db()
    game = await db.fetch_all("select game_id from USERGAMEDATA where user_id = :user_id", values={"user_id":user_id})
    if game:
        return list(map(dict,game))
    else:
        abort(404)

@app.route("/startgame/<int:user_id>",methods=["POST"])
async def startGame(user_id):
    db = await _get_db()
    userCheck = await db.fetch_one("select user_id from USERDATA where user_id = :user_id",values={"user_id":user_id})
    file = open('correct.json')
    data = json.load(file)
    random.choice(data)
    secret_word = random.choice(data)
    dbData= {"user_id":user_id,"secret_word":secret_word}
    try:
     gameID = await db.execute("""
     insert into USERGAMEDATA(user_id,secret_word) VALUES(:user_id,:secret_word)
     """,dbData)
    except sqlite3.IntegrityError as e:
     abort(409,e)
    res={"game_id": gameID}
    return res,201,{"Location": f"/startgame/{gameID}"}


@app.errorhandler(404)
def not_found(e):
    return {"error": "The resource could not be found"}, 404




