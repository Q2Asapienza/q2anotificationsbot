#!/bin/bash
cd "$(dirname "$0")"

#output date
date +"%d/%m/%Y %H:%M"

#update repository to last version
git fetch --all
git reset --hard origin/master

#set every file executable
chmod -R 777 ./

#run script
./main.py