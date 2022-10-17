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
    except sqlite3.sqlite3.IntegrityError as e:
     abort(409,e)

    return Response("User Registration Successful!",status=201)

@app.route("/login/",methods=["GET"])
async def loginUser() -> Response:
    db = await _get_db()
    data =  request.authorization
    try:
     userDet = await db.fetch_one("select * from USERDATA where user_name = :user and user_pass= :pass",values={"user": data['username'], "pass": data['password']})
     if userDet is None: 
        return Response("Unsuccessful authentication",status=401,headers=dict({'WWW-Authenticate': 'Basic realm="Access to staging site"'}))
    except sqlite3.sqlite3.IntegrityErrshor as e:
        abort(409,e)
    return Response(json.dumps({"authenticated":True,"user ID": userDet[2]}),status=200)
    






@app.route("/games/<int:id>", methods=["GET"])
async def all_games(id):
    db = await _get_db()
    game = await db.fetch_all("SELECT * FROM games WHERE user_id = :id", values={"id": id})
    if game:
        return dict(game)
    else:
        abort(404)

@app.route("/startgame/<int:user_id>",methods=["POST"])
async def startGame(user_id):
    db = await _get_db()
    file = open('correct.json')
    data = json.load(file)
    random.choice(data)
    secret_word = random.choice(data)
    dbData= {"user_id":user_id,"secret_word":secret_word}
    try:
     gameID = await db.execute("""
     insert into USERGAMEDATA(user_id,secret_word) VALUES(:user_id,:secret_word)
     """,dbData)
    except sqlite3.sqlite3.IntegrityError as e:
     abort(409,e)
    res={"game_id": gameID}
    return res,201,{"Location": f"/startgame/{gameID}"}


@app.errorhandler(404)
def not_found(e):
    return {"error": "The resource could not be found"}, 404




