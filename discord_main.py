import time
from taiiwobot import taiiwobot, discord, config, util
import sys

if len(sys.argv) == 2:
    config = config.Config(config_location=sys.argv[1], key="discord_config")
else:
    config = config.Config(key="discord_config")
# use discord as our server protocol
server = discord.Discord(config)
# Start the bot!
taiiwobot.TaiiwoBot(server, config)
