#!/bin/bash

if ! [ "$(pgrep -f 'python3 bot.py')" ]
then
  echo "Bot not running. Starting up."
  cd /path/to/trailbot
  screen -dmS bot python3 bot.py >> bot.log
fi
