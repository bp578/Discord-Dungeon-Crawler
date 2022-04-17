import discord
import time
from discord.ext import tasks
import random

# store state; basically all data
class GameState:
	def __init__(self):
		self.updates = [] # list of callbacks (functions) that are run every 5 seconds. use state.register_update(cb) to add an update function
		self.reaction_handlers = {} # dictionary of message to callback (function). callback is run every time a reaction appears on that message.
		self.running_encounters = [] # list of encounters that are currently running. contains instances of Encounter class
		self.players = [] # list of registered players
		# get data from file
		lines = []
		with open("player_data.txt", "r") as file:
			lines = file.readlines()
		for line in lines:
			player_id = line.split(" ")[0]
			self.players.append(player_id)

	# change data for given player to given value
	def change_player_data(self, player, data):
		id = str(player.id)
		if id not in self.players: self.players.append(id)
		data = " ".join([str(val) for val in data.values()])
		lines = []
		with open("player_data.txt", "r") as file:
			lines = file.readlines()
		found = False
		for i in range(len(lines)):
			other_id = lines[i].split(" ")[0]
			if other_id == id:
				lines[i] = id + " " + data + "\n"
				with open("player_data.txt", "w") as file:
					file.writelines(lines)
				found = True
		if not found:
			with open("player_data.txt", "a") as file:
				file.write(id + " " + data + "\n")

	# delete all data for given player
	def delete_player_data(self, player):
		id = str(player.id)
		self.players.remove(id)
		lines = []
		with open("player_data.txt", "r") as file:
			lines = file.readlines()

		with open("player_data.txt", "w") as file:
			for line in lines:
				other_id = line.split(" ")[0]
				if other_id != id:
					file.write(line)

	# get data as dictionary for given player
	def get_player_data(self, player):
		# update from file
		lines = []
		with open("player_data.txt", "r") as file:
			lines = file.readlines()
		for line in lines:
			numbers = line.split(" ")
			other_id = numbers[0]
			print(other_id)
			print(player.id)
			if other_id == str(player.id):
				data = {
						"HP:": numbers[1],
						"ATK:": numbers[2],
						"DEF:": numbers[3],
						"SPD:": numbers[4],
						"STR:": numbers[5],
						"INT:": numbers[6],
						"REG:": numbers[7],
						"RMP:": numbers[8],
				}
				return data

	# add function to list of update functions
	def register_update(self, cb):
		self.updates.append(cb)
	@tasks.loop(seconds=5.0)
	async def run_updates(self):
		for update in self.updates:
			await update()

	def add_reaction_handler(self, message: discord.Message, callback):
		self.reaction_handlers[message] = callback
	def del_reaction_handler(self, message: discord.Message):
		self.reaction_handlers.pop(message)
	async def handle_reaction(self, reaction, user):
		if reaction.message in self.reaction_handlers:
			await self.reaction_handlers[reaction.message](reaction, user)

	def new_encounter(self, player: discord.Member, msg: discord.Message):
		# if player is already in an encounter, return false
		for encounter in self.running_encounters:
			if encounter.player == player:
				return False
		encounter = Encounter(player, msg, self, randEnemy())
		self.running_encounters.append(encounter)
		self.reaction_handlers[msg] = encounter.handle_reaction
		self.updates.append(encounter.update)
		return True
	def close_encounter(self, player: discord.Member):
		found = False
		for encounter in self.running_encounters:
			if encounter.player == player:
				found = True
				self.running_encounters.remove(encounter)
				self.del_reaction_handler(encounter.msg)
				self.updates.remove(encounter.update)
		return found

ENCOUNTER_INFO = """
{0} vs. {1}
{1}:
 - HP: {2}
 - DMG: {3}
{0}:
 - CLASS: {7}
 - HP: {4}
 - DMG: {5}
{6}
"""

class Enemy:
  def __init__(self, name='', HP=0, DMG=0):
    self.name = name
    self.HP = HP
    self.DMG = DMG

  #getters
  def getName(self):
    return self.name

  def getHP(self):
    return self.HP

  def getDMG(self):
    return self.DMG

#Instantiate a random enemy object.
def randEnemy():
  goblin = Enemy("Goblin", 20, 1)
  ogre = Enemy("Ogre", 30, 10)
  skeleton = Enemy("Skeleton", 10, 5)
  rat = Enemy("Rat", 10, 1)
  spider = Enemy("Spider", 15, 8)
  
  enemyList = [goblin, ogre, skeleton, rat, spider]
  enemy = enemyList[random.randrange(len(enemyList))]
  return enemy

PLAYER_BASE_HP = 100
PLAYER_DMG = 5
PLAYER_CLASS = "???"

class Encounter:
  def __init__(self, player: discord.Member, msg: discord.Message, state: GameState, enemy):
    self.activated = False
    self.msg = msg
    self.player = player
    self.player_hp = PLAYER_BASE_HP
    self.enemy_name = enemy.getName()
    self.enemy_hp = enemy.getHP()
    self.enemy_dmg = enemy.getDMG()
    self.last_action = "Make your move"
    self.state = state

  async def handle_reaction(self, reaction, user):
    if user == self.player:
      if reaction.emoji == "👊":
        await self.player_hit()
        time.sleep(3)
        await reaction.remove(self.player)
        await self.enemy_hit()
    if reaction.emoji == "✌️":
			  await self.leave_encounter(self.player.mention + " peaced out ✌️")

  async def update(self):
	  if not self.activated:
		  self.activated = True
		  await self.update_text()
		  await self.msg.add_reaction("👊")
		  await self.msg.add_reaction("✌️")

  async def update_text(self):
	  text = ENCOUNTER_INFO.format(
				self.player.mention,
				self.enemy_name,
				self.enemy_hp,
				self.enemy_dmg,
				self.player_hp,
				PLAYER_DMG,
				self.last_action,
				PLAYER_CLASS
		)
	  await self.msg.edit(content=text)

  async def player_hit(self):
    self.enemy_hp -= PLAYER_DMG
    if self.enemy_hp <= 0:
      items = ["health potion", "gold", "mana potion"]
      item = items[random.randrange(0,3)]
      await self.leave_encounter("You have slain the beast and gained: " + item)
    else:
      self.last_action = self.player.mention + " hit " + self.enemy_name + " for " + str(PLAYER_DMG) + " HP!"
      await self.update_text()

  async def enemy_hit(self):
    if self.enemy_hp > 0:
      self.player_hp -= self.enemy_dmg
      self.last_action = self.enemy_name + " hit " + self.player.mention + " for " + str(self.enemy_dmg) + " HP!"
      await self.update_text()
    
		

  async def leave_encounter(self, msg):
	  self.state.close_encounter(self.player)
	  await self.msg.edit(content=msg)
