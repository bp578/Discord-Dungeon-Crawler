import discord

class GameState:
	def __init__(self):
		self.running_encounters = []
		self.reaction_handlers = {}

	def new_encounter(self, player: discord.Member, msg: discord.Message):
		encounter = Encounter(player, msg)
		self.running_encounters.append(encounter)
		self.reaction_handlers[msg] = encounter.handle_reaction
	def close_encounter(self, player: discord.Member):
		for encounter in self.running_encounters:
			if encounter.player == player:
				self.running_encounters.remove(encounter)
	def add_reaction_handler(self, message: discord.Message, callback):
		self.reaction_handlers[message] = callback
	
	def handle_reaction(self, reaction):
		if reaction.message in self.reaction_handlers:
			self.reaction_handlers[reaction.message](reaction)


class Encounter:
	ENEMY_BASE_HP = 20
	PLAYER_BASE_HP = 100
	ENEMY_DMG = 1
	PLAYER_DMG = 5
	def __init__(self, player: discord.Member, msg: discord.Message):
		self.msg = msg
		self.player = player
		self.player_hp = self.PLAYER_BASE_HP
		self.enemy_hp = self.ENEMY_BASE_HP
	def handle_reaction(self, reaction):
		print(reaction)
