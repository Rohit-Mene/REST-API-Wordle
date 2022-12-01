#!/bin/sh

sqlite3 ../var/user.db < ../share/user.sql
sqlite3 ../var/primary/mount/game.db < ../share/game.sql

mkdir .//var/primary
mkdir .//var/secondary1
mkdir .//var/secondary2

