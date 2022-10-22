Gage Giovanni
Rohit Mene
Sean McCarthy
# cpsc449-project-wordle

# DB Script Excecution Steps -
   1) GO to path /Project1/bin
   2) Run command sh init.sh
   3) Go to path /Project1/var
   4) Run command  sqlite3 project1.db
   5) Run command .tables  to check if tables are created

-----------------------
API DOCUMENTATION-
1) User registration:
  http POST http://localhost:5000/registeruser/ user:='{"name":"<name>","pass":"<pass>"}'

  where <name> is the username of the new user and <pass> is the password of the new user

    Sample Output:
        {
            "message": "User Registration Successful!",
            "user_id": 1
        }

2) User Login:
  http --form --auth <name>:<pass> --auth-type basic GET http://localhost:5000/login/

  where <name> is the user name of the user trying to login and <pass > is the password of the user trying to login

    2a) If given a valid username and password for an existing password:

        Sample Output:
            {
                "authenticated": true
            }

    2b) If given an invalid username or password:

        Sample Output:
            {
                "response": "Unsuccessful authentication"
            }
        
3) Start a game:
  http POST http://localhost:5000/startgame/ user:='{"user_id":<user_id>}'

  where <user_id> is the id number of the user starting the game

      Sample Output:
          {
              "game_id": 1
          }

4)Retrieve a list of all active games for a user
  http GET http://127.0.0.1:5000/games/<:id> 
  
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

5) Get the state of a game
  http GET http://localhost:5000/gamestate/ game:='{"game_id":<game_id>}'

  where <game_id> is the id number of an existing game
  
    5a) If the given game_id corresponds to a completed game, it returns a JSON object in the form of:
    
    Sample Output:

        {
            "guesses_used": 5,
            "victory": false
        }

        Output Format:
            guesses_used {int}: number of guesses made before the given game ended
            victory {boolean}: represents the outcome of the given game. true for a win, false for a loss

    5b) If the given game_id corresponds to an active game, it returns a JSON object in the form of:

    Sample Output:

        {
            "game_id": 1,
            "guesses": [
                {
                    "correct_guess": false,
                    "correct_position": "01",
                    "correct_letter_incorrect_spot": "34",
                    "guessed_word": "moler",
                    "guesses_remaining": 5,
                    "valid": true
                }
            ],
            "guesses_remaining": 5,
            "user": 1
        }

        Output Format:
            game_id {int}: id of the given game
            guesses_remaining {}: total guesses remaining in the given game
            user {int}: id of the user who started the given game
            guesses {list}: list of all the guesses made in the given game, where:
                correct_guess {boolean}: states whether the guess matched the secret word
                correct_position {string}: each index in the guess containing a correct letter in the correct spot
                correct_letter_incorrect_spot {string}: each index in the guess containing a correct letter in the incorrect spot
                guessed_word {string}: the word that was guessed
                guesses_remaining {int}: number of remaining guesses after this guess was made
                valid {boolean}: boolean representing whether the guess was in the valid word list or not


6) Make a guess in an active game:
  http PUT http://127.0.0.1:5000/guess/ guess_to_make:='{"game_id":<game_id>,"guess":"<guess>"}'

  Use the JSON format after URL to enter input data for this api. Enter the game ID where <game_id> is and enter guess word where <guess> is.
    
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


