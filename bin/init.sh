#!/bin/sh

echo "Creating sqlite databases"
#sqlite3 var/user.db < share/user.sql
sqlite3 var/primary/mount/game.db < share/game.sql




