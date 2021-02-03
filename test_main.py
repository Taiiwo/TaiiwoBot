import time
from taiiwobot import taiiwobot, test_server, config

config = config.Config(key="test_config")
# use IRC as our server protocol
server = test_server.TestServer(config or {})
# Start the bot!
taiiwobot.TaiiwoBot(server, config)
