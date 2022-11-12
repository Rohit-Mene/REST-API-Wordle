import dataclasses
import sqlite3
from quart import Quart,g,request,abort
import databases
from quart_schema import QuartSchema
import uuid

app = Quart(__name__)
QuartSchema(app)

#DB Connection
async def _get_db():
    db = getattr(g, "_sqlite_db", None)
    if db is None:
        db = g._sqlite_db = databases.Database('sqlite+aiosqlite:/var/game.db')
        await db.connect()
    return db

#DB Disconnect 
@app.teardown_appcontext
async def close_connection(exception):
    db = getattr(g, "_sqlite_db", None)
    if db is not None:
         await db.disconnect()

@dataclasses.dataclass
class Guess:
    game_id: int
    guess: str

#API for starting a new game
@app.route("/startgame/",methods=["POST"])
async def startGame():
    db = await _get_db()
    data =  request.authorization

    secret_word= await db.fetch_one("select correct_word from CORRECTWORD ORDER BY RANDOM() LIMIT 1;")
    game_id = uuid.uuid1().hex
    if secret_word:
     dbData= {"game_id":game_id,"secret_word":secret_word[0],"user_name":data['username']}
    
     try:
      gameID = await db.execute("""
      insert into USERGAMEDATA(game_id,user_name,secret_word) VALUES(:game_id,:user_name,:secret_word)
      """,dbData)
     except sqlite3.IntegrityError as e:
      abort(409,e)
     res={"game_id": game_id}
     return res,201,{"Location": f"/startgame/{gameID}"}

# API for getting the state of an existing game
@app.route("/gamestate/", methods=["GET"])
async def gamestate():
    # contact db
    db = await _get_db()
    # retrieve input JSON
    userDet = await request.get_json()
    game_id = userDet.get('game').get('game_id')
    # retrieve db game date and guess data for the given game_id
    gamestate = await db.fetch_all("select * from USERGAMEDATA where game_id = :game_id", values={"game_id": game_id})
    guesses = await db.fetch_all("select guess_num, guessed_word from guess where game_id = :game_id", values={"game_id": game_id})

    if gamestate:
        gameinfo = list(map(dict,gamestate))
        status = gameinfo[0]['game_sts']
        guessList = list(map(dict,guesses))

        # if the game is still active, retrieve list of guesses
        if status == 0:
            secret = gameinfo[0]['secret_word']
            guessInfo = []
            
            # retrieve correctness of each guess
            for guess in guessList:
                correct_spot_list = ""
                correct_letter_list = ""
                guessed_word = guess['guessed_word']

                for i in range(0, len(guessed_word)):
                    if guessed_word[i] in secret:
                        if guessed_word[i] == secret[i]:
                            correct_spot_list = correct_spot_list + str(i)
                        else:
                            correct_letter_list = correct_letter_list + str(i)

                correct = False
                if guess == secret:
                    correct = True

                guessDict = {
                    'guessed_word': guessed_word,
                    'valid': True,
                    'correct_guess': correct,
                    'guesses_remaining': 5 - guess['guess_num'],
                    'correct_letter_incorrect_spot': correct_letter_list,
                    'correct_position': correct_spot_list
                }

                guessInfo.append(guessDict)

            # return game info and guess data
            liveGame = {
                'game_id': game_id,
                'user': gameinfo[0]['user_name'],
                'guesses_remaining': gameinfo[0]['guess_cnt'],
                'guesses': guessInfo
            }

            return liveGame

        # if the game is no longer active, return the victory status and guesses used
        else:
            guessesUsed = len(guesses)
            finalGuess = guessList[guessesUsed - 1]['guessed_word']
            secret = gameinfo[0]['secret_word']

            # determine the outcome of the game and set victory accordingly
            victory = True if finalGuess == secret else False

            return {"victory": victory, "guesses_used": guessesUsed}
    else:
        abort(404)

#api for making a guess to an active game
@app.route("/guess/", methods=["PUT"])
async def make_guess():
    #contact db
    db = await _get_db()
    #retrieve json
    data = await request.get_json()
    #store game id input
    guess_id={'game_id': data.get('guess_to_make').get('game_id')}
    #store word guessed
    string_guess = {'guess': data.get('guess_to_make').get('guess')}
    #check to see if word entered is a valid guess
    try:
        valid_check = await db.fetch_val(
            """
                SELECT word_id FROM VALIDWORD WHERE EXISTS(SELECT word_id FROM VALIDWORD WHERE valid_word = :guess)
            """, 
            string_guess,
        )
    except sqlite3.IntegrityError as e:
        abort(500, e)
    #check to see if word entered is not on valid list
    try:
        invalid_check = await db.fetch_val(
            """
                SELECT * FROM VALIDWORD WHERE NOT EXISTS(SELECT word_id FROM VALIDWORD WHERE valid_word = :guess)
            """, 
            string_guess,
        )
    except sqlite3.IntegrityError as e:
        abort(500, e)
    #obtain number of guesses left
    try:
        gueses_left = await db.fetch_val(
            """
                SELECT guess_cnt FROM USERGAMEDATA WHERE game_id = :game_id
            """,
            guess_id,
        )     
    except sqlite3.IntegrityError as e:
        abort(500, e)
    #determine if the game is an active game
    try:
        completed_game = await db.fetch_val(
            """
            SELECT game_sts FROM USERGAMEDATA WHERE game_id = :game_id
            """,
            guess_id,
        )
    except sqlite3.IntegrityError as e:
        abort(500, e)    
    #obtain secret word
    try:
        secret_word = await db.fetch_val(
            """
            SELECT secret_word FROM USERGAMEDATA WHERE game_id = :game_id
            """,
            guess_id,
        )
        #test if guess is secret word, and make sure game is active
        if data.get('guess_to_make').get('guess') == secret_word and completed_game == False:
            try:
                #if correct word decrease guess remaining and change game state to false
                await db.execute(
                    """ 
                        UPDATE USERGAMEDATA SET guess_cnt = guess_cnt - 1, game_sts = TRUE WHERE game_id = :game_id;
                    """,
                    guess_id
                )
            except sqlite3.IntegrityError as e:
                abort(500, e)
            #insert relevant data from guess into the guess table to track the valid guess made
            try:
                insert_tuple = {'game_id':data.get('guess_to_make').get('game_id'), 'guess_num' :(6 - gueses_left + 1), 'guessed_word':data.get('guess_to_make').get('guess')}
                await db.execute(
                    """ 
                        INSERT INTO guess(game_id, guess_num, guessed_word) VALUES(:game_id, :guess_num, :guessed_word)                        
                    """,insert_tuple,
                )
            except sqlite3.IntegrityError as e:
                abort(500, e)
            #if correct return 
            return {"correct_word": "TRUE"},201
        #if guess is not correct but valid 
        elif valid_check and completed_game == False and gueses_left > 1:
            try:
                #decrease guesses remaining
                await db.execute(
                    """ 
                        UPDATE USERGAMEDATA SET guess_cnt = guess_cnt - 1 WHERE game_id = :game_id;
                    """,
                    guess_id
                )
            except sqlite3.IntegrityError as e:
                abort(500, e)
            #insert the valid guess into the guess table to track the guess
            try:
                insert_tuple = {'game_id':data.get('guess_to_make').get('game_id'), 'guess_num' :6 - gueses_left, 'guessed_word':data.get('guess_to_make').get('guess')}
                await db.execute(
                    """ 
                        INSERT INTO guess(game_id, guess_num, guessed_word) VALUES(:game_id, :guess_num, :guessed_word)                        
                    """,insert_tuple,
                )
            except sqlite3.IntegrityError as e:
                abort(500, e)
            #obtain new guess count for return data
            guess_word = str(data.get('guess_to_make').get('guess'))
            #the next section is the logic to obtain what letters are in the correct spot
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
            return {"valid":"TRUE" ,  "guess_remaining ": str(gueses_left - 1), "correct_position" : spot_to_string , "correct_letter_incorrect_spot ": letter_to_string},201
        #if no guesses remian in game
        elif valid_check and completed_game == False and gueses_left <= 1:
            try:
                #change game state to TRUE meaning game is over 
                await db.execute(
                    """ 
                        UPDATE USERGAMEDATA SET game_sts = TRUE WHERE game_id = :game_id;
                    """,
                    guess_id
                )
            except sqlite3.IntegrityError as e:
                abort(500, e)
            #return statement letting player know they are out of guesses
            try:
                insert_tuple = {'game_id':data.get('guess_to_make').get('game_id'), 'guess_num' :6 - gueses_left, 'guessed_word':data.get('guess_to_make').get('guess')}
                await db.execute(
                    """ 
                        INSERT INTO guess(game_id, guess_num, guessed_word) VALUES(:game_id, :guess_num, :guessed_word)                        
                    """,insert_tuple,
                )
            except sqlite3.IntegrityError as e:
                abort(500, e)    
            return {"guess_rem" : "0","game_sts": "TRUE"},201
        #if the word guessed is invalid let the user know it is not valid and they must guess again
        elif invalid_check:
            return {"valid": "FALSE", "guess_rem" : str(gueses_left)},201 
        
    except sqlite3.IntegrityError as e:
        abort(409, e)

@app.route("/games/", methods=["GET"])
async def all_games():
    #connect to db
    db = await _get_db()
    data =  request.authorization
    user_name = {"user_name": data['username']}
    #select all active games for a single user
    game = await db.fetch_all(
        """
            select game_id from USERGAMEDATA where user_name = :user_name AND game_sts = FALSE
        """, user_name, 
    
    )
    if game:
        return list(map(dict,game)),201
    else:
        abort(404)


@app.errorhandler(404)
def not_found(e):
    return {"error": "The resource could not be found"}, 404
