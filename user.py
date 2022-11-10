import dataclasses
import json
import sqlite3
from quart import Quart,g,request,abort,Response
import databases
from quart_schema import QuartSchema

app = Quart(__name__)
QuartSchema(app)

#DB Connection
async def _get_db():
    db = getattr(g, "_sqlite_db", None)
    if db is None:
        db = g._sqlite_db = databases.Database('sqlite+aiosqlite:/var/user/mount/user.db')
        await db.connect()
    return db

#DB Disconnect 
@app.teardown_appcontext
async def close_connection(exception):
    db = getattr(g, "_sqlite_db", None)
    if db is not None:
         await db.disconnect()

# API for User Registration for the game
@app.route("/registeruser/",methods=["POST"])
async def registerUser():
    db = await _get_db()
    userDet = await request.get_json()
    userDetMap={'name': userDet.get('user').get('name'),'password': userDet.get('user').get('pass')}

    try:
        #Passes the username and password given by user 
     userId= await db.execute("""INSERT INTO USERDATA(user_name,user_pass) VALUES(:name,:password)""",userDetMap,)
     #Takes in userID received from the user to generate a response
     response = {"message":"User Registration Successful!","user_id":userId}

    except sqlite3.IntegrityError as e:
     abort(409,e)
     
    return response,201

#API for User Login for authentication
@app.route("/login/",methods=["GET"])
async def loginUser():
    db = await _get_db()
    data =  request.authorization
    app.logger.debug(data)
    if data:
     try:
        #Find the User details
      userDet = await db.fetch_one("select * from USERDATA where user_name = :user and user_pass= :pass",values={"user": data['username'], "pass": data['password']})
      if (userDet is None): 
         return Response(json.dumps({"response":"Unsuccessful authentication"}),status=401,headers=dict({'WWW-Authenticate': 'Basic realm="Access to staging site"'}), content_type="application/json")
     except sqlite3.IntegrityError as e:
        abort(409,e)
        return Response(json.dumps({"authenticated":True}),status=200, content_type="application/json")
    else:
        return Response(json.dumps({"response":"Invalid Request!"}), status=400, content_type="application/json")