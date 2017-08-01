import sqlite3
import json
import math
import sys

voters = {}
total = {'weight':0,'reward':0}

conn = sqlite3.connect('bot.db')
c = conn.cursor()

c.execute('''SELECT postid, weight, voter, reward FROM votes WHERE reward > 0''')
votes = c.fetchall()
for vote in votes:
  weight = vote[1]
  voter = vote[2]
  reward = vote[3]
  if voter in voters:
    voters[voter]['weight'] += weight
    voters[voter]['reward'] += reward
  else:
    voters[voter] = {'weight': weight, 'reward': reward}

  total['weight'] += weight
  total['reward'] += reward

for account,voter in voters.items():
  print(account+':')
  rewardperweight = voter['reward'] / voter['weight']
  print('Reward per weight: '+str(rewardperweight))
  print('Percent of weight: '+str((voter['weight']*100)/total['weight']))
  print('Percent of reward: '+str((voter['reward']*100)/total['reward']))
