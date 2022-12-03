# cpsc449-project-wordle
## Part 4
1)Rohit Mene
2)Debdyuti Das
3)Apeksha Shah
4)Nicholas Fonseca

# Setup and Operation Guide
## Setup
### 1) Copy nginxconfig to /etc/nginx/sites-enabled:<br />
       sudo cp nginxconfig /etc/nginx/site-enabled
       
### 2) Run the directory creation shell file from path   REST-API-Wordle/bin :<br />
       sh dircreation.sh

### 3) Ensure litefs has proper permissions<br />
      chmod 777 litefs

## Operation

### 4) Run foreman:<br />
       foreman start
      
### 5) Run init script from the path REST-API-Wordle/ :<br />
       bin/init.sh




## Troubleshooting
```
### Run this command in case of redis failure
    redis-cli shutdown
```

-----------------------
API DOCUMENTATION-
### 1) User registration:<br />
 #### http POST http://tuffix-vm/registeruser/ user:='{"name":"<name>","pass":"<pass>"}'
  where <name> is the username of the new user and <pass> is the password of the new user

    Sample Output:
        {
            "message": "User Registration Successful!",
            "user_id": 1
        }

### 2) User Login:<br />
 #### http --form --auth name:pass --auth-type basic GET http://tuffix-vm/login/

  where <name> is the user name of the user trying to login and <pass > is the password of the user trying to login

####    2a) If given a valid username and password for an existing password:<br />

        Sample Output:
            {
                "authenticated": true
            }

  ####  2b) If given an invalid username or password:<br />

        Sample Output:
            {
                "response": "Unsuccessful authentication"
            }
        
### 3) Start a game:<br />
 #### http --auth name:pass --auth-type basic POST http://tuffix-vm/startgame/


      Sample Output:
          {
              "game_id": "f6514c5060a311ed83c79b083e15e21b"
          }

### 4)Retrieve a list of all active games for a player:<br />
 #### http --auth name:pass --auth-type basic GET http://tuffix-vm/games/

  Returns dictionary of all active games by a single user with the user name
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

### 5)Get the state of a game:<br />
 #### http --auth name:pass --auth-type basic GET http://tuffix-vm/gamestate/ game:='{"game_id":<game_id>}'

  where <game_id> is the id number of an existing game
  
 ####   5a) If the given game_id corresponds to a completed game, it returns a JSON object in the form of:<br />
    
    Sample Output:

        {
            "guesses_used": 5,
            "victory": false
        }

        Output Format:
            guesses_used {int}: number of guesses made before the given game ended
            victory {boolean}: represents the outcome of the given game. true for a win, false for a loss

 ####   5b) If the given game_id corresponds to an active game, it returns a JSON object in the form of:<br />

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


### 6) Make a guess in an active game:<br />
####  http --auth name:pass --auth-type basic PUT http://tuffix-vm/guess/ guess_to_make:='{"game_id":<game_id>,"guess":"<guess>"}'

  Use the JSON format after URL to enter input data for this api. Enter the game ID where <game_id> is and enter guess word where <guess> is.
    
 ####   6a) If the word is the correct word it returns a JSON object in the form of:<br />      

    Sample Output:
        {
        "correct_word": "TRUE"
        }   
            Output format.
                correct_word states if the word entered is the secret word for the specified game.

 ####   6b) If the word is valid but not correct it returns a JSON object in the form of:<br /> 

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

 ####   6c) If you run out of guesses without guessing the correct word you return a JSON object in the form of:<br />

    Sample Output:
        {
        "game_sts": "TRUE",
        "guess_rem": "0"
        }
            Output Format.
                Game_sts is false when the game is still active and true when game is no longer active.

  ####  6d) If the guess is invalid it returns a JSON object in the form of:<br /> 

    Sample Output:
        {
        "guess_rem": "#",
        "valid": "FALSE"
        }
            Output Format.
                valid represents if the word guessed is a valid guess.
                guess_rem represents the number of guesses remaining.

 ###   7) Leaderboard API for posting the results of a game:<br />    
 #### http POST http://localhost:5050/leaderboard/post uname=<str> guesses:=<int: less than 6> win:=<bool>
    Sample API - http POST http://localhost:5050/leaderboard/post uname="rohit" guesses:=6 win:=false
               - http POST http://localhost:5050/leaderboard/post uname="rohit" guesses:=6 win:=false   
    Note that, as the url is internal, the url is local:5050 rather than tuffix-vm

     Response will be 200 if accepted, 400 if data is wrong

 ###   8) Leaderboard API for getting top 10:<br />
####  http GET http://tuffix-vm/leaderboard

      Response will be 200 with payload {"leaders":<list of top 10>}

