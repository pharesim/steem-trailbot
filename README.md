# steem-trailbot
A bot to vote-follow a list of curators on steem

Follow curators with variable or fixed percentage, do not allow self-votes including known dual accounts, blacklist, keep track of votes and rewards

Requires piston, sqlite3

Set up database:
sqlite3 bot.db < botdb.txt

Includes a simple failover script (bot.sh) to run as a cronjob, you need to set the path to the bot in the script.
