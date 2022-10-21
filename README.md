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

#http GET http://127.0.0.1:5000/games/<:id> returns dictionary of all active games by a single user with id <:id>


http --form PUT http://127.0.0.1:5000/guess/ game_id=8 guess="kneed"
If the word is the correct word it returns a JSON object in the form of,        

    {correct_word: TRUE}

If the word is valid but not correct it returns a JSON object in the form of, 

    "{valid :TRUE ,  guess_remaining :2, correct position :, correct letter incorrect spot :1}"

correct position is an array containing the index's of letters in the correct position, correct letter incorrect spot is an array of the index's of letters that 
are in the guess word but in the wrong position in the guess word. 

If you run out of guesses without guessing the correct word you return a JSON object in the form of 

       "{guess_rem : 0, game_sts: TRUE}"

Game_sts is false when the game is still active and true when game is no longer active

If the guess is invalid it returns a JSON object in the form of 

    {valid: FALSE, guess_rem : # }"


http GET http://127.0.0.1:5000/games/6

This returns all games currently active by user (in this case 6) it returns a JSON object in the form of 

     {
        "game_id": 4
    },
    {
        "game_id": 8
    },
    {
        "game_id": 13
    }

