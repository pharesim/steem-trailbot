from piston import Steem
from piston.blockchain import Blockchain
from piston.amount import Amount
from piston.block import Block
from pistonbase import transactions
from pistonapi.steemnoderpc import SteemNodeRPC
import sqlite3
import json
import math
import sys
import time

votewith = 'accountname'
wif = '5...'
node = 'ws://steemd.pevo.science:8090'

follow = {
  'curator1': 0.1, # follow with 10% of curator's weight
  'curator2': 10   # follow with 10% fixed
}

clones = {
  'curator1':['sockpuppet1','sockpuppet2']
}

except_authors = [
  'spammer',
  'plagiarizer'
]

client = Steem(node=node,wif=wif)
blockchain = Blockchain()
rpc = SteemNodeRPC(node)
conn = sqlite3.connect('bot.db')
c = conn.cursor()

def main(lastblock):
  thisblock = blockchain.get_current_block_num()
  if lastblock == thisblock:
    return thisblock

  for op in blockchain.ops(lastblock+1,thisblock):
    type = op['op'][0]
    op = op['op'][1]
    op['type'] = type
    if op['type'] == 'vote':
      followvote(op)
    if op['type'] == 'curation_reward':
      reward(op)

  return thisblock

def followvote(op):
  if op['weight'] <= 1 or op['voter'] not in follow or op['author'] in except_authors or op['author'] == op['voter'] or (op['voter'] in clones and op['au$
    return False

  print("Valid vote found by "+op['voter']+" ("+str(op['weight'])+")")
  postid = '@'+op['author']+'/'+op['permlink']
  post = client.get_post(postid)
  dovote = True
  for v in post['active_votes']:
    if v['voter'] == votewith:
      print('already voted on '+postid)
      dovote = False

  if dovote == True and (str(post['last_payout']) != '1970-01-01 00:00:00' or post['max_accepted_payout'] == Amount('0.000 SBD')):
    print(postid+' is not a curation rewarding post')
    dovote = False

  if dovote == True:
    fweight = follow[op['voter']]
    weight = fweight
    if op['weight'] == 0:
      weight = 0
    elif fweight < 1:
      weight = math.ceil(op['weight']*fweight)/100
    if weight >= 0:
      if weight == 0.01:
        weight = 0.02

      nop = transactions.Vote(
          **{"voter": votewith,
             "author": op["author"],
             "permlink": op["permlink"],
             "weight": int(weight*100)}
      )
      castvote(transactions.Operation(nop))

      print('Voted on '+postid+' following '+op["voter"]+' with '+str(weight)+'%')
      try:
        with conn:
          c.execute('''INSERT OR IGNORE INTO votes (postid, weight, voter, reward) VALUES (?,?,?,?)''', (postid, weight, op['voter'], 0,))
      except:
        print('vote not saved')


def reward(op):
  if op['curator'] != votewith:
    return False

  print("Valid reward found")
  postid = '@'+op['comment_author']+'/'+op['comment_permlink']
  try:
    with conn:
      c.execute('''UPDATE votes SET reward=? WHERE postid=?''', (op['reward'][:-6],postid,))
  except:
    print('vote not found, no reward saved')

def castvote(op):
  expiration = transactions.formatTimeFromNow(180)
  ref_block_num, ref_block_prefix = transactions.getBlockParams(rpc)
  tx     = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                         ref_block_prefix=ref_block_prefix,
                                         expiration=expiration,
                                         operations=[op])
  tx = tx.sign([wif])
  dobroadcast(tx)

def dobroadcast(tx):
  try:
    rpc.broadcast_transaction(tx.json(), api="network_broadcast")
    time.sleep(3)
  except Exception as e:
    print(e)
    time.sleep(3)
    dobroadcast(tx)

if __name__ == "__main__":
  repeats = 0
  lastblock = blockchain.get_current_block_num()
  while True:
    tmp = lastblock

    lastblock = main(lastblock)

    if lastblock == tmp:
      repeats += 1
    else:
      repeats = 0

    if repeats >= 25:
      sys.exit()

    time.sleep(3)
