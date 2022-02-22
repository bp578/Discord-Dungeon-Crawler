import discord

class GameState:
	def __init__(self):
		self.updates = []
		self.reaction_handlers = {}
		self.running_encounters = []

	def register_update(self, cb):
		self.updates.append(cb)
	async def run_updates(self):
		for update in self.updates:
			await update()

	def add_reaction_handler(self, message: discord.Message, callback):
		self.reaction_handlers[message] = callback
	async def handle_reaction(self, reaction):
		if reaction.message in self.reaction_handlers:
			await self.reaction_handlers[reaction.message](reaction)
	
	def new_encounter(self, player: discord.Member, msg: discord.Message):
		# if player is already in an encounter, return false
		for encounter in self.running_encounters:
			if encounter.player == player:
				return False
		encounter = Encounter(player, msg, self)
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
				self.reaction_handlers.pop(encounter.msg)
				self.updates.remove(encounter.update)
		return found

ENCOUNTER_INFO = """
{0} vs. {1}
{1}:
 - HP: {2}
 - DMG: {3}
{0}:
 - HP: {4}
 - DMG: {5}
{6}
"""
ENEMY_BASE_HP = 20
PLAYER_BASE_HP = 100
ENEMY_DMG = 1
PLAYER_DMG = 5
class Encounter:
	def __init__(self, player: discord.Member, msg: discord.Message, state: GameState):
		self.activated = False
		self.msg = msg
		self.player = player
		self.player_hp = PLAYER_BASE_HP
		self.enemy_hp = ENEMY_BASE_HP
		self.last_action = "Make your move"
		self.state = state
	
	async def handle_reaction(self, reaction):
		if await reaction.users().find(lambda u : u == self.player):
			if reaction.emoji == "👊":
				await self.player_hit()
				await reaction.remove(self.player)
			if reaction.emoji == "✌️":
				await self.leave_encounter()
	
	async def update(self):
		if not self.activated:
			self.activated = True
			await self.update_text()
			await self.msg.add_reaction("👊")
			await self.msg.add_reaction("✌️")

	async def update_text(self):
		text = ENCOUNTER_INFO.format(
			self.player.mention,
			"Goblin",
			self.enemy_hp,
			ENEMY_DMG,
			self.player_hp,
			PLAYER_DMG,
			self.last_action
		)
		await self.msg.edit(content=text)
	
	async def player_hit(self):
		self.enemy_hp -= PLAYER_DMG
		self.last_action = self.player.mention + " hit Goblin for " + str(PLAYER_DMG) + " HP!"
		await self.update_text()
	async def enemy_hit(self):
		self.player_hp -= ENEMY_DMG
	
	async def leave_encounter(self):
		self.state.close_encounter(self.player)
		await self.msg.edit(content=self.player.mention + " peaced out ✌️")
