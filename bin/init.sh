#!/bin/sh

echo "Creating data and mount folders"
# mkdir -p var/primary/mount
# mkdir -p var/secondary1/mount
# mkdir -p var/secondary2/mount

# mkdir -p var/primary/data
# mkdir -p var/secondary1/data
# mkdir -p var/secondary2/data

echo "Creating sqlite databases"
sqlite3 var/user.db < share/user.sql
sqlite3 var/primary/mount/game.db < share/game.sql




