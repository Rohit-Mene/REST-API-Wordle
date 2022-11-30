user: hypercorn user --reload --debug --bind user.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG

leaderBoard: hypercorn leaderBoard --reload --debug --bind leaderBoard.local.gd:5050 --access-logfile - --error-logfile - --log-level DEBUG

primary: ./bin/litefs -config ./etc/primary.yml
secondary1: ./bin/litefs -config ./etc/secondary1.yml
secondary2: ./bin/litefs -config ./etc/secondary2.yml