import collections
import dataclasses
from re import S
import sqlite3
from quart import Quart,g,request,abort
import databases
import toml
import textwrap
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

    return "User Registration Successful!",201

@app.route("/login/",methods=["POST"])
async def registerUser():
    db = await _get_db()
    data = await request.form
    dat_tup={'name':data['name'],'password':data['pass']}

    try:
     await db.execute("""INSERT INTO USERDATA(user_name,user_pass) VALUES(:name,:password)""",dat_tup,)
    except sqlite3.sqlite3.IntegrityError as e:
     abort(409,e)

    return "User Registration Successful!",201




