import os
import inspect

from taiiwobot.plugin import Plugin


class Reload(Plugin):
    def __init__(self, bot):
        self.bot = bot
        self.interface = bot.util.Interface(
            "reload", "Reloads a plugin's code for dev purposes", [], self.reload
        ).listen()

    def unload(self):
        print("You can't reload this plugin using itsself for obvious reasons...")

    def reload(self, message, query):
        # me only!
        if message.author != self.bot.config["owner"]:
            self.bot.msg(message.target, "Access Denied!", follows=message)
            return
        for plugin in self.bot.plugins:
            if type(plugin).__name__.lower() == query.lower():
                # unload plugin
                plugin_name = type(plugin).__name__
                plugin.unload()
                self.bot.plugins.remove(plugin)
                self.bot.msg(message.target, "Plugin unloaded..", follows=message)
                # load the plugin
                break
        for root, dirs, files in os.walk("plugins"):
            # for each py file in the plugins folder
            for file in files:
                if file[-3:] == ".py" and file[:-3].lower() == query.lower():
                    # import it
                    namespace = {}
                    with open(
                        os.path.join(root, file), encoding="utf-8"
                    ) as plugin_file:
                        code = compile(
                            plugin_file.read(), os.path.join(root, file), "exec"
                        )
                        exec(code, namespace)
                    plugin = False
                    for key in namespace:
                        if key.lower() == query.lower():
                            plugin = namespace[key]
                    plugin.__module__ = "Plugin." + file[:-3]
                    # init the class and add it to the plugin list
                    if plugin:
                        self.bot.plugins.append(plugin(self.bot))
                        self.bot.msg(message.target, "Plugin loaded!", follows=message)
                    else:
                        self.bot.msg(
                            message.target, "Plugin not found.", follows=message
                        )
