# cpsc449-project-wordle

# DB Script Excecution Steps -
   1) GO to path /Project1/bin
   2) Run command sh init .sh
   3) Go to path /Project1/var
   4) Run command  sqlite3 project1.db
   5) Run command .tables  to check if tables are created

-----------------------
API DOCUMENTATION-
1) User registration:
  #http POST http://localhost:5000/registeruser/ user:='{"name":"rohit","pass":"mene"}'

2) User Login -
  #http --form --auth rohit:mene --auth-type basic GET http://localhost:5000/login/

3) Start a game:
  #http POST http://localhost:5000/startgame/<user_id>

4)Retrieve a list of all active games for a plater
  #http GET http://127.0.0.1:5000/games/<:id> 
  
  Returns dictionary of all active games by a single user with id <:id>
    Sample Output:
        {
            "game_id": 4
        },
        {
            "game_id": 8
        },
        {
            "game_id": 13
        }
            Output Format.
                game_id represents a game that is active for the player in question.

5) #http GET http://localhost:5000/gamestate/ game:='{"game_id":1}'

6) Make a guess in an active game:
  http PUT http://127.0.0.1:5000/guess/ guess_to_make:='{"game_id":"#","guess":"     "}'
  Use the JSON format after URL to enter input data for this api. Enter the game ID where # is and enter guess word in blank string.
    
    6a) If the word is the correct word it returns a JSON object in the form of,        

    Sample Output:
        {
        "correct_word": "TRUE"
        }   
            Output format.
                correct_word states if the word entered is the secret word for the specified game.

    6b) If the word is valid but not correct it returns a JSON object in the form of, 

    Sample Output:
        {
        "correct_letter_incorrect_spot ": "",
        "correct_position": "",
        "guess_remaining ": "",
        "valid": "TRUE"
        }
            Output format.
                valid states if a word entered is a valid guess
                guess_remaining indicates the number of guesses left in the game before it ends.
                correct_position is an array containing the index's of letters in the correct position. 
                correct_letter_incorrect_spot is an array of the index's of letters that are in the guess word but in the wrong position in the guess word. 

    6c) If you run out of guesses without guessing the correct word you return a JSON object in the form of 

    Sample Output:
        {
        "game_sts": "TRUE",
        "guess_rem": "0"
        }
            Output Format.
                Game_sts is false when the game is still active and true when game is no longer active.

    6d) If the guess is invalid it returns a JSON object in the form of 

    Sample Output:
        {
        "guess_rem": "#",
        "valid": "FALSE"
        }
            Output Format.
                valid represents if the word guessed is a valid guess.
                guess_rem represents the number of guesses remaining.


