import time
from taiiwobot import taiiwobot, discord, config, util
import sys

if len(sys.argv) == 2:
    config = config.get_config(config_location=sys.argv[1])
else:
    config = config.get_config()
# use discord as our server protocol
server = discord.Discord(config['discord_config'])
# Start the bot!
taiiwobot.TaiiwoBot(server, config)
