
import dataclasses
from http.client import HTTPResponse, responses
import json
import random
from re import S
import sqlite3
from wsgiref import headers
from quart import Quart,g,request,abort,Response
import databases

from quart_schema import QuartSchema,validate_request
from sqlalchemy import false
app = Quart(__name__)
QuartSchema(app)


async def _get_db():
    db = getattr(g, "_sqlite_db", None)
    if db is None:
        db = g._sqlite_db = databases.Database('sqlite+aiosqlite:/var/project1.db')
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
    userDet = await request.get_json()
    dat_tup={'name': userDet.get('user').get('name'),'password': userDet.get('user').get('pass')}

    try:
     userId= await db.execute("""INSERT INTO USERDATA(user_name,user_pass) VALUES(:name,:password)""",dat_tup,)
     response = {"message":"User Registration Successful!","user_id":userId}
    except sqlite3.IntegrityError as e:
     abort(409,e)
     
    return response,201

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
     return Response(json.dumps({"authenticated":True}),status=200)
    else:
        return Response("Invalid Request!", status=400)
    
@app.route("/gamestate/<int:game_id>", methods=["GET"])
async def gamestate(game_id):
    db = await _get_db()
    gamestate = await db.fetch_all("select * from USERGAMEDATA where game_id = :game_id", values={"game_id": game_id})
    if gamestate:
        guesses = await db.fetch_all("select guess_num, guessed_word from guess where game_id = :game_id", values={"game_id": game_id})
        gameinfo = gamestate + guesses
        return list(map(dict,gameinfo))
    else:
        abort(404)

@dataclasses.dataclass
class Guess:
    game_id: int
    guess: str

@app.route("/guess/", methods=["PUT"])
@validate_request(Guess)
async def make_guess(data):
    db = await _get_db()
    #data = await request.form
    #guess_made={'game_id':data['game_id'], 'guess' :data['guess']}
    guess_made = dataclasses.asdict(data)
    file = open('valid.json')
    word_list = json.load(file)
    #obtain secret word
    try:
        gueses_left = await db.fetch_val(
            """
            SELECT guess_cnt FROM USERGAMEDATA WHERE game_id = :game_id
            """,
            guess_made,
        )
    except sqlite3.IntegrityError as e:
        abort(500, e)
    try:
        completed_game = await db.fetch_val(
            """
            SELECT game_sts FROM USERGAMEDATA WHERE game_id = :game_id
            """,
            guess_made,
        )
    except sqlite3.IntegrityError as e:
        abort(500, e)    
    try:
        secret_word = await db.fetch_val(
            """
            SELECT secret_word FROM USERGAMEDATA WHERE game_id = :game_id
            """,
            guess_made,
        )
        #test if guess is correct
        if data[':guess'] == secret_word and completed_game == False:
            try:
                #if correct word decrease guess remaining and change game state to false
                await db.execute(
                    """ 
                        UPDATE USERGAMEDATA SET guess_cnt = guess_cnt - 1, game_sts = TRUE WHERE game_id = :game_id;
                    """,
                    guess_made
                )
            except sqlite3.IntegrityError as e:
                abort(500, e)
            try:
                insert_tuple = {'game_id':data['game_id'], 'guess_num' :(6 - gueses_left + 1), 'guessed_word':data['guess']}
                await db.execute(
                    """ 
                        INSERT INTO guess(game_id, guess_num, guessed_word) VALUES(:game_id, :guess_num, :guessed_word)                        
                    """,insert_tuple,
                )
            except sqlite3.IntegrityError as e:
                abort(500, e)
            #if correct return 
            return Response(json.dumps("{correct_word: TRUE}"),status=201)
        #if guess is not correct but valid 
        elif data[':guess'] in word_list and completed_game == False and gueses_left > 1:
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
            try:
                insert_tuple = {'game_id':data['game_id'], 'guess_num' :6 - gueses_left, 'guessed_word':data['guess']}
                await db.execute(
                    """ 
                        INSERT INTO guess(game_id, guess_num, guessed_word) VALUES(:game_id, :guess_num, :guessed_word)                        
                    """,insert_tuple,
                )
            except sqlite3.IntegrityError as e:
                abort(500, e)
            #obtain new guess count to return
            guess_word = str(data[':guess'])
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
            return Response(json.dumps('{valid :TRUE ,  guess_remaining :' + str(gueses_left - 1) + ', correct position :' + spot_to_string + ', correct letter incorrect spot :' + letter_to_string + '}'),status=201)
        #if guess is not on valid list tell the user to try a different word
        elif gueses_left <= 1:
            try:
                #no guesses left 
                await db.execute(
                    """ 
                        UPDATE USERGAMEDATA SET game_sts = TRUE WHERE game_id = :game_id;
                    """,
                    guess_made
                )
            except sqlite3.IntegrityError as e:
                abort(500, e)
            return Response(json.dumps("{guess_rem : 0, game_sts: TRUE}"),status=201)
        else:
            return Response(json.dumps("{valid: FALSE, guess_rem :"+ str(gueses_left) + "}"),status=204) 
        
    except sqlite3.IntegrityError as e:
        abort(409, e)


@app.route("/games/<int:user_id>", methods=["GET"])
async def all_games(user_id):
    db = await _get_db()
    game = await db.fetch_all("select game_id from USERGAMEDATA where user_id = :user_id AND game_sts = FALSE", values={"user_id":user_id})
    if game:
        return Response(json.dumps(list(map(dict,game))), status=201)
    else:
        abort(404)

@app.route("/startgame/<int:user_id>",methods=["POST"])
async def startGame(user_id):
    db = await _get_db()
    userCheck = await db.fetch_one("select user_id from USERDATA where user_id = :user_id",values={"user_id":user_id})
    if userCheck == None:
        res={"response":"Not Found!"}
        return res,404

    secret_word= await db.fetch_one("select correct_word from CORRECTWORD ORDER BY RANDOM() LIMIT 1;")

    dbData={"err":"No Data"}
    if secret_word:
     dbData= {"user_id":user_id,"secret_word":secret_word[0]}
    
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




