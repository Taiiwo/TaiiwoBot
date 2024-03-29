import os
import time
import importlib.machinery
from . import util, config, plugin


class TaiiwoBot:
    def __init__(self, server, config):
        self.server = server
        self.config = config
        # expose server functions
        self.on = server.on
        self.msg = server.msg
        self.menu = server.menu
        self.prompt = server.prompt
        self.util = util
        self.plugins = []
        # load our plugins
        @server.on("ready", "root")
        def server_ready(d):
            if len(self.plugins) == 0:
                self.plugins = self.load_plugins()

        # run the blocking function
        self.server.start()

    def load_plugins(self):
        # get all the plugins from the plugin folder
        plugins = []
        for root, dirs, files in os.walk("plugins"):
            # for each py file in the plugins folder
            for file in files:
                if file[-3:] == ".py":
                    if "plugin_blacklist" in self.config:
                        if file[:-3] in self.config["plugin_blacklist"]:
                            continue
                    # import it
                    plugin = __import__(
                        os.path.join(root, file[:-3])
                        .replace("/", ".")
                        .replace("\\", ".")
                    )
                    plugin = getattr(plugin, file[:-3])
                    # find all the plugin classes
                    for attr in dir(plugin):
                        # ignore the _ attrs for safety
                        if attr[0] == "_":
                            continue
                        # if the attr is a unintitialized class
                        if isinstance(getattr(plugin, attr), type):
                            # if the class is based on the plugin class
                            if getattr(plugin, attr).__bases__[0] == plugin.Plugin:
                                # init the class and add it to the plugin list
                                plugins.append(getattr(plugin, attr)(self))
                                break
        return plugins
