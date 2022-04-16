class Plugin:
    @property
    def name(self):
        return self.__module__.split(".")[-1]

    def unload(self):
        if hasattr(self, "interface"):
            self.bot.server.unload_command(self.interface)
            self._unloaded = True
            del self.interface

    def mention(self, user):
        return user

    def code_block(self, text):
        return text

    # decorators for authenticated functions
    def authenticated(f):
        def handler(plugin, message, *args, **kwargs):
            if plugin.bot.server.is_mod(message):
                return f(plugin, message, *args, **kwargs)
            else:
                # this should actually throw a runtime error imo
                plugin.bot.msg(
                    message.target,
                    "You don't have permission to use this command!",
                    follows=message,
                )
                return False

        return handler

    def owner(f):
        def handler(plugin, message, *args, **kwargs):
            if plugin.bot.server.is_owner(message):
                return f(plugin, message, *args, **kwargs)
            else:
                # this should actually throw a runtime error imo
                plugin.bot.msg(
                    message.target,
                    "You don't have permission to use this command!",
                    follows=message,
                )
                return False

        return handler
