import os
from discord.ext import commands, tasks
import discord
import gamestate
import enemyImages as ei
from gamestate import GameState

bot = commands.Bot(
	command_prefix="!",
	case_insensitive=True,
	help_command=None
)
bot.author_id = 487258918465306634  # Change to your discord id!!!

state = GameState()

@bot.event
async def on_ready():
	print("I'm in")
	print(bot.user)  # Prints the bot's username and identifier

@bot.event
async def on_reaction_add(reaction, user):
	if user != bot.user:
		await state.handle_reaction(reaction, user)

@bot.command(profile=['user'])
async def profile(ctx,member : discord.Member):
    embed = discord.Embed(title = member.name, color = discord.Color.blue())
    embed.add_field(name = "ID", value = member.id, inline = True)
    embed.set_thumbnail(url = member.avatar_url)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
	await ctx.reply("`pong!`")

@bot.command()
async def help(ctx):
  embed = discord.Embed(title = "Need help?", color = discord.Color.blue(), description = """
ng: Begin a new game 
eg: End current game 
stats: Display your current stats
register: store your stats and in-game progress so that your progress saves between each encounter
	""")
	
  embed.add_field(name = "Note", value = "Remember that \"!\" precedes every command",  inline = True)
  embed.set_author(name="Discord Bot Game", icon_url="https://icon-library.com/images/new-discord-icon/new-discord-icon-19.jpg")
  user = ctx.author
  await user.send(embed=embed)

@bot.command()
async def ng(ctx):
  #beginGame is called once the player picks a class. 
  async def beginGame():
    state.newEnemy()
    start_msg = await ctx.reply("A new adventure begins in a dark dungeon...")
    # start encounter
    encounter_embed = discord.Embed(title = f"{ctx.author.display_name} has initiated an encounter", description = "You have come upon a savage beast...", color = discord.Color.red())
    encounter_embed.set_image(url=ei.dungeonImage)
    encounter_msg = await ctx.send(embed=encounter_embed)
    if not state.new_encounter(ctx.author, encounter_msg):
      await start_msg.edit(content="You are already in an encounter....")
      await encounter_msg.delete()

  classSelectContents = '''React to pick your class:
   1. Warrior ⚔️
   2. Mage ✨
   3. Rogue 🗡
   4. Tank 🛡️
   5. Marksman 🏹
  '''
  #classSelectMsg is the first thing sent upon starting a new game.
  classSelectMsg = await ctx.send(classSelectContents)
  await classSelectMsg.add_reaction("⚔️")
  await classSelectMsg.add_reaction("✨")
  await classSelectMsg.add_reaction("🗡")
  await classSelectMsg.add_reaction("🛡️")
  await classSelectMsg.add_reaction("🏹")

  #This function checks what emoji the player reacted with and changes their class accordingly
  async def check(reaction, user):
    if user == ctx.author and reaction.emoji in ["⚔️","✨","🗡","🛡️","🏹"]:
      if reaction.emoji == "⚔️":
        await ctx.send("You picked: Warrior")
        await classSelectMsg.delete()
        await beginGame()
        gamestate.PLAYER_CLASS = "Warrior"
      elif reaction.emoji == "✨":
        await ctx.send("You picked: Mage")
        await classSelectMsg.delete()
        await beginGame()
        gamestate.PLAYER_CLASS = "Mage"
      elif reaction.emoji == "🗡":
        await ctx.send("You picked: Rogue")
        await classSelectMsg.delete()
        await beginGame()
        gamestate.PLAYER_CLASS = "Rogue"
      elif reaction.emoji == "🛡️":
        await ctx.send("You picked: Tank")
        await classSelectMsg.delete()
        await beginGame()
        gamestate.PLAYER_CLASS = "Tank"
      elif reaction.emoji == "🏹":
        await ctx.send("You picked: Marksman")
        await classSelectMsg.delete()
        await beginGame()
        gamestate.PLAYER_CLASS = "Marksman"
  state.add_reaction_handler(classSelectMsg, check)

@bot.command()
async def eg(ctx):
	if state.close_encounter(ctx.author):
		await ctx.reply("You have cut your own life short. Better luck on your next adventure.")
	else:
		await ctx.reply("You are not currently in an encounter...")

data = {
  "HP:": 100,
  "ATK:": 5,
  "DEF:": 5,
  "SPD:": 5,
  "STR:": 5,
  "INT:": 0,
  "REG:": 0,
  "RMP:": 0,
}

async def bag(ctx):
    def __init__(self, level = 1):
        self.level = 1
        self.contents = list()
        self.qties = list() 
  	
    return
    def inBag(self, itemName):
        
        pos = None
        found = False
        if len(self.contents) > 0:
            i = 0
            while not found and i < len(self.contents): 
                found = itemName.lower() == self.contents[i].getName().lower()
                if not found: 
                    i += 1
        if found: 
            pos = i
        return pos
    def putIn(self, item, qty):
       
        added = False
        if len(self.contents) < self.size:
            pos = self.inBag(item.getName())
            if pos != None: 
                self.qties[pos] += 1
            else:
                self.contents.append(item) 
                self.qties.append(qty) 
            added = True
        return added
    def getContentsSize(self):
        return len(self.contents)
    def getSize(self):
        return self.size
    def isFull(self):
        return self.getContentsSize() == self.size
    def getItemAt(self, pos):
        
        return self.contents[pos]
    def getQtyAt(self, pos):
        
        return self.qties[pos]
    def takeOut(self, itemName, qty):
        
        takenOut = None
        pos = self.inBag(itemName)
        if pos != None:
            if qty <= self.qties[pos]: 
                takenOut = self.contents[pos] 
                self.qties[pos] -= qty 
            else:
                takenOut = "You don't have enough of that." 
            if self.qties[pos] == 0: 
               
                del self.contents[pos]
                del self.qties[pos]
        return takenOut
    def availableInBag(self):
        '''Returns a sample the contents of the bag as a list of "item" objects.
        Will be used to loot monsters.'''
        return self.contents

@bot.command()
async def delete_register(ctx):
    if str(ctx.author.id) in state.players:
        state.delete_player_data(ctx.author)
        await ctx.reply("Data successfully deleted")
    else:
        await ctx.reply("You didn't register yet!")

@bot.command()
async def register(ctx):
    if str(ctx.author.id) in state.players:
        await ctx.reply("You already registered before")
    else:
        state.change_player_data(ctx.author, data)
        await ctx.reply("You successfully registered")

@bot.command()
async def stats(ctx):
	# check if player has registered
    if str(ctx.author.id) in state.players:
		# get data
        data = state.get_player_data(ctx.author)
		# format data into string
        string = ""
        for key, val in data.items():
            string += key + str(val) + "\n"
        await ctx.reply(string)
    else:
        await ctx.reply("You need to register with `!register` first")

@state.run_updates.before_loop
async def before_updates(self):
	await bot.wait_until_ready()

state.run_updates.start()
token = "OTYxMDU2OTkyMjEyOTQyODY5.YkzcEg.XeS5Z_ao08bDEBHCUHE1z1OoYkY"
bot.run(token)

