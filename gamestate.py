import discord
import time
from discord.ext import tasks
import random
import enemyImages as ei

# store state; basically all data
class GameState:
  def __init__(self):
    self.updates = [] # list of callbacks (functions) that are run every 5 seconds. use state.register_update(cb) to add an update function
    self.reaction_handlers = {} # dictionary of message to callback (function). callback is run every time a reaction appears on that message.
    self.running_encounters = [] # list of encounters that are currently running. contains instances of Encounter class
    self.players = [] # list of registered players
		# get data from file
    self.enemy = randEnemy()

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

  def startWarrior(self, player):
    warriorStats = {
      "CLASS: ": "Warrior",
			"HP: ": 125,
			"ATK: ": 4,
			"DEF: ": 10,
			"SPD: ": 5,
			"STR: ": 15,
			"INT: ": 0,
      "CurrentHP: ": 125
    }
    self.change_player_data(player, warriorStats)

  def startMage(self, player):
    mageStats = {
      "CLASS: ": "Mage",
			"HP: ": 75,
			"ATK: ": 8,
			"DEF: ": 5,
			"SPD: ": 3,
			"STR: ": 0,
			"INT: ": 10,
      "CurrentHP: ": 75
    }
    self.change_player_data(player, mageStats)

  def startRogue(self, player):
    rogueStats = {
      "CLASS: ": "Rogue",
			"HP: ": 100,
			"ATK: ": 6,
			"DEF: ": 5,
			"SPD: ": 20,
			"STR: ": 5,
			"INT: ": 0,
      "CurrentHP: ": 100
    }
    self.change_player_data(player, rogueStats)

  def startTank(self, player):
    tankStats = {
      "CLASS: ": "Tank",
			"HP: ": 150,
			"ATK: ": 3,
			"DEF: ": 20,
			"SPD: ": 0,
			"STR: ": 20,
			"INT: ": 0,
      "CurrentHP: ": 150
    }
    self.change_player_data(player, tankStats)

  def startMarksman(self, player):
    marksmanStats = {
      "CLASS: ": "Marksman",
			"HP: ": 80,
			"ATK: ": 5,
			"DEF: ": 0,
			"SPD: ": 10,
			"STR: ": 5,
			"INT: ": 5,
      "CurrentHP: ": 80
    }
    self.change_player_data(player, marksmanStats)
  
        
  def newEnemy(self):
    self.enemy = randEnemy()

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
            "CLASS: ": numbers[1],
						"HP: ": numbers[2],
						"ATK: ": numbers[3],
						"DEF: ": numbers[4],
						"SPD: ": numbers[5],
						"STR: ": numbers[6],
						"INT: ": numbers[7],
            "CurrentHP: ": numbers[8]
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
    encounter = Encounter(player, msg, self, self.enemy)
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

class Enemy:
  def __init__(self, name, HP, DMG, image):
    self.name = name
    self.HP = HP
    self.DMG = DMG
    self.image = image
    self.status = ""
    self.statusTimer = 0
  
  #getters
  def getName(self):
    return self.name

  def getHP(self):
    return self.HP

  def getDMG(self):
    return self.DMG

  def getImage(self):
    return self.image

  def getStatusTimer(self):
    return self.statusTimer

  def getStatus(self):
    return self.status

  #setters
  def decrementStatusTimer(self):
    self.statusTimer -= 1

  def setStatusTimer(self, timer):
    self.statusTimer = timer
    
  def setStatus(self, status):
    self.status = status

  
#Instantiate an enemy object
def randEnemy():
  goblin = Enemy("Goblin", 25, 5, ei.goblinImage)
  ogre = Enemy("Ogre", 40, 10, ei.ogreImage)
  skeleton = Enemy("Skeleton", 20, 3, ei.skeletonImage)
  rat = Enemy("Rat", 15, 1, ei.ratImage)
  spider = Enemy("Spider", 15, 8, ei.spiderImage)
  
  enemyList = [goblin, ogre, skeleton, rat, spider]
  enemy = enemyList[random.randrange(len(enemyList))]
  return enemy
    
class Encounter:
  def __init__(self, player: discord.Member, msg: discord.Message, state: GameState, enemy):
    self.activated = False
    self.msg = msg
    self.player = player
    self.playerData = state.get_player_data(player)
    self.player_hp = float(self.playerData["CurrentHP: "])
    self.abilityCD = 0
    self.playerAtkInit = float(self.playerData["ATK: "])
    self.isGuarding = False
    self.enemy = enemy
    self.enemy_name = enemy.getName()
    self.enemy_hp = enemy.getHP()
    self.enemy_dmg = enemy.getDMG()
    self.enemy_image = enemy.getImage()
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
			  await self.leave_encounter(discord.Embed(title = f"FLED!", description = f"{self.player.mention} peaced out ✌️", color = discord.Color.green()))
      
    #Warrior ability: Berserk
    #Increases ATK by 50% at the cost of 10% HP
    if reaction.emoji == "⚔️" and self.abilityCD <= 0:
        atkGained = float(self.playerData["ATK: "]) * 0.5 
        hpLost = self.player_hp * 0.1
        self.playerData["ATK: "] = float(self.playerData["ATK: "]) * 1.5 
        self.player_hp *= 0.9
        self.last_action = self.player.mention + " used Berserk, sacrificing " + str(hpLost) + " HP and increasing ATK by " + str(atkGained)
        await self.update_text()
        time.sleep(3)
        await reaction.remove(self.player)
        await self.enemy_hit()
        self.abilityCD = 3
    elif reaction.emoji == "⚔️" and self.abilityCD > 0:
        self.last_action = "That ability is on cooldown! It will be available in " + str(self.abilityCD) + " turns."
        await self.update_text()
        await reaction.remove(self.player)
      

    #Mage ability: Binding Hex
    #Binds enemy in place for 3 turns, making them unable to attack
    if reaction.emoji == "✨" and self.abilityCD <= 0:
        self.enemy.setStatus("Binded")
        self.enemy.setStatusTimer(3)
        self.last_action = self.player.mention + " used Binding Hex, preventing " + self.enemy_name + " from attacking"
        await self.update_text()
        time.sleep(3)
        await reaction.remove(self.player)
        await self.enemy_hit()
        self.abilityCD = 10
    elif reaction.emoji == "✨" and self.abilityCD > 0:
        self.last_action = "That ability is on cooldown! It will be available in " + str(self.abilityCD) + " turns."
        await self.update_text()
        await reaction.remove(self.player)  

    #Rogue ability: Deadly Strike
    #A powerful strike does double damage if the enemy has less than 50% HP but 1 damage if the enemy has 50% HP or more.
    if reaction.emoji == "🗡" and self.abilityCD <= 0:
        enemyMaxHP = self.enemy.getHP()
        if float(self.enemy_hp/enemyMaxHP) < 0.5:
          self.enemy_hp -= float(self.playerData["ATK: "]) * 2
          if self.enemy_hp <= 0:
            items = ["health potion", "gold", "mana potion"]
            item = items[random.randrange(0,3)]
            await self.leave_encounter(discord.Embed(title = f"VICTORY!", description = f"You have slain the beast and gained: {item}", color = discord.Color.green()))
          else:
            self.last_action = self.player.mention + " used Deadly Strike and landed a critical strike on " + self.enemy_name + ", dealing " + str(float(self.playerData["ATK: "]) * 2) + " damage!"
            await self.update_text()
            time.sleep(3)
            await reaction.remove(self.player)
            await self.enemy_hit()
            self.abilityCD = 5
        else:
          self.enemy_hp -= 1
          if self.enemy_hp <= 0:
            items = ["health potion", "gold", "mana potion"]
            item = items[random.randrange(0,3)]
            await self.leave_encounter(discord.Embed(title = f"VICTORY!", description = f"You have slain the beast and gained: {item}", color = discord.Color.green()))
          else:
            self.last_action = self.player.mention + " used Deadly Strike on " + self.enemy_name + " but couldn't reach a vital, dealing 1 damage..."
            await self.update_text()
            time.sleep(3)
            await reaction.remove(self.player)
            await self.enemy_hit()
            self.abilityCD = 5
    elif reaction.emoji == "🗡" and self.abilityCD > 0:
        self.last_action = "That ability is on cooldown! It will be available in " + str(self.abilityCD) + " turns."
        await self.update_text()
        await reaction.remove(self.player) 
      

    #Tank Ability: Guard Counter
    #Take 90% less damage from the next attack and counter attack, dealing 50% of the enemy's attack
    if reaction.emoji == "🛡️" and self.abilityCD <= 0:
        self.isGuarding = True
        self.last_action = self.player.mention + " used Guard Counter, raising their shield."
        await self.update_text()
        time.sleep(3)
        await self.enemy_hit()
        self.abilityCD = 3
        time.sleep(3)
        self.enemy_hp -= self.enemy_dmg * 1.5
        if self.enemy_hp <= 0:
            items = ["health potion", "gold", "mana potion"]
            item = items[random.randrange(0,3)]
            await self.leave_encounter(discord.Embed(title = f"VICTORY!", description = f"You have slain the beast and gained: {item}", color = discord.Color.green()))
        else:
          self.last_action = self.player.mention + " slams their shield against " + self.enemy_name + ", dealing " + str(self.enemy_dmg * 1.5) + " damage!"
          await self.update_text()
          time.sleep(3)
          self.isGuarding = False
          await reaction.remove(self.player)
    elif reaction.emoji == "🛡️" and self.abilityCD > 0:
        self.last_action = "That ability is on cooldown! It will be available in " + str(self.abilityCD) + " turns."
        await self.update_text()
        await reaction.remove(self.player) 

    #Marksman Ability: Headshot
    #An attack that has a 10% chance to instantly kill the enemy but a 90% chance to miss
    if reaction.emoji == "🏹" and self.abilityCD <= 0:
        chance = random.randrange(1,11)
        if chance == 7:
          self.enemy_hp = 0
          self.last_action = self.player.mention + " used Headshot and successfully landed a killing blow on " + self.enemy_name + "!"
          await self.update_text()
          time.sleep(3)
          await reaction.remove(self.player)
          items = ["health potion", "gold", "mana potion"]
          item = items[random.randrange(0,3)]
          await self.leave_encounter(discord.Embed(title = f"VICTORY!", description = f"You have slain the beast and gained: {item}", color = discord.Color.green()))
        else:
          self.last_action = self.player.mention + " used Headshot but completely missed!"
          await self.update_text()
          time.sleep(3)
          await reaction.remove(self.player)
          await self.enemy_hit()
          self.abilityCD = 1
    elif reaction.emoji == "🏹" and self.abilityCD > 0:
      self.last_action = "That ability is on cooldown! It will be available in " + str(self.abilityCD) + " turns."
      await self.update_text()
      await reaction.remove(self.player) 
          


  async def update(self):
    if not self.activated:
      self.activated = True
      await self.update_text()
      await self.msg.add_reaction("👊")
      await self.msg.add_reaction("✌️")
      
      if self.playerData["CLASS: "] == "Warrior":
        await self.msg.add_reaction("⚔️")
      elif self.playerData["CLASS: "] == "Mage":
        await self.msg.add_reaction("✨")
      elif self.playerData["CLASS: "] == "Rogue":
        await self.msg.add_reaction("🗡")
      elif self.playerData["CLASS: "] == "Tank":
        await self.msg.add_reaction("🛡️")
      elif self.playerData["CLASS: "] == "Marksman":
        await self.msg.add_reaction("🏹")
      
  async def update_text(self):    
    userStats = f'''
CLASS: `{self.playerData["CLASS: "]}`
HP: `{self.player_hp}`
DMG: `{self.playerData["ATK: "]}`
    '''
    
    enemyStats = f'''
HP: `{self.enemy_hp}`
DMG: `{self.enemy_dmg}`
    '''

    embed = discord.Embed(title = f"{self.player.display_name}'s battle against {self.enemy_name}", description = "A savage beast stands in your way", color = discord.Color.red())
    embed.set_image(url=self.enemy_image)
    embed.add_field(name=f"{self.player.display_name}:", value=userStats, inline=True)
    embed.add_field(name=f"{self.enemy_name}:", value=enemyStats, inline=True)
    embed.add_field(name=f"LAST ACTION:", value=self.last_action, inline=False)
    await self.msg.edit(embed=embed)

  async def player_hit(self):
    self.enemy_hp -= float(self.playerData["ATK: "])
    if self.enemy_hp <= 0:
      items = ["health potion", "gold", "mana potion"]
      item = items[random.randrange(0,3)]
      await self.leave_encounter(discord.Embed(title = f"VICTORY!", description = f"You have slain the beast and gained: {item}", color = discord.Color.green()))
    else:
      self.last_action = self.player.mention + " hit " + self.enemy_name + " for " + str(self.playerData["ATK: "]) + " HP!"
      await self.update_text()
    
  async def enemy_hit(self):
    if self.enemy_hp > 0 and self.enemy.getStatus() != "Binded":
      if self.isGuarding == True:
        self.player_hp -= self.enemy_dmg * 0.1
      else:
        self.player_hp -= self.enemy_dmg
        
      self.playerData["CurrentHP: "] = self.player_hp
      self.last_action = self.enemy_name + " hit " + self.player.mention + " for " + str(self.enemy_dmg) + " HP!"
      await self.update_text()
    elif self.enemy_hp > 0 and self.enemy.getStatus() == "Binded":
      self.last_action = self.enemy_name + " cannot move!"
      self.enemy.decrementStatusTimer()
      await self.update_text()

    if self.player_hp <= 0:
      await self.leave_encounter(discord.Embed(title = f"RIP", description = f"{self.player.mention} was slain in battle. Register again.", color = discord.Color.red()))
      self.state.delete_player_data(self.player)
      
    if self.enemy.getStatusTimer() <= 0:
      self.enemy.setStatus("")
    
    if self.abilityCD > 0:
      self.abilityCD -= 1

  async def leave_encounter(self, embed):
    self.playerData["ATK: "] = float(self.playerAtkInit)
    self.state.change_player_data(self.player, self.playerData)
    self.state.close_encounter(self.player)
    await self.msg.edit(embed=embed)
