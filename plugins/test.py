from taiiwobot.plugin import Plugin


class Test(Plugin):
    def __init__(self, bot):
        print("test plugin init")
        self.bot = bot
        self.interface = bot.util.Interface(
            "test",
            "This command does some action",
            [],
            self.some_func,
            subcommands=[
                bot.util.Subcommand(
                    "owner-test", "checks if user is an owner", [], self.owner,
                ),
                bot.util.Subcommand(
                    "mod-test", "checks if user is a mod", [], self.mod,
                ),
            ],
        ).listen()

    def some_func(self, message, *args):
        self.bot.msg(message.target, "test complete", follows=message)

    @Plugin.owner
    def owner(self, message):
        self.bot.msg(message.target, "You are an owner", follows=message)

    @Plugin.authenticated
    def mod(self, message):
        self.bot.msg(message.target, "You are a mod", follows=message)
