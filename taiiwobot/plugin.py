class Plugin:
    @property
    def name(self):
        return self.__module__.split(".")[-1]

    def unload(self):
        if hasattr(self, "interface"):
            self._unloaded = True
            del self.interface

    def mention(self, user):
        return user

    def code_block(self, text):
        return text
