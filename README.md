# Discord Bot Game

Setting the bot up

Install Python 3.5 or 3.6. The latest version of Python that works is 3.6.8, which can be installed from https://www.python.org/downloads/release/python-368/. If you are running on Windows, then be sure to check the box that will add Python to PATH.

Clone this repository. Rename config.py.example to config.py and settings.py.example to settings.py, and fill in the fields inside config.py. To change some gameplay-related settings, edit settings.py.
Dependencies

Our Discord bot game has hard dependencies on discord.py and dotenv. You can run pip install -r requirements.txt to install the required dependencies. Note that the bot uses an older version of discord.py, but with an additional fix to accommodate Discord's API update.

Running the bot

You must first create a new bot account at https://discordapp.com/developers/applications/me. Put the bot's token inside config.py. Next, add the bot to your server using the OAuth2 link https://discord.com/api/oauth2/authorize?client_id=961056992212942869&permissions=8&scope=bot .If you are running on Windows, run python bot.py or double-click run.bat to launch the auto-restarter (it will restart the bot if it crashes for whatever reason). If you are running on a UNIX-based system, run either python3 bot.py, or python3.5 bot.py or python3.6 bot.py, depending on the version of Python that you are using.
