from taiiwobot import Plugin
import time
import random


class Cookies(Plugin):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.util.get_db()["cookies"]
        self.interface = bot.util.Interface(
            "cookie",  # plugin name
            "CookiEconomy plugin",  # plugin description
            [],
            self.some_func,  # main function
            subcommands=[  # list of subcommands
                bot.util.Interface(
                    "balance",  # invoked with $template sub <args/flags>
                    "Check your cookie balance",  # subcommand description
                    [],
                    self.balance,  # subcommand function
                ),
                bot.util.Interface(
                    "summon",  # invoked with $template sub <args/flags>
                    "Summons a cookie, for testing and displays of admin dominance",  # subcommand description
                    [],
                    self.summon,  # subcommand function
                ),
            ],
        ).listen()  # sets the on message callbacks and parses messages

        @bot.on("message")
        def spawn_cookie(message):
            if random.randint(1, 100) <= 1:
                self.bot.msg(
                    message.target,
                    "A cookie appeared",
                    reactions=(("🍪", self.collect_cookie),),
                    delete_after=60,
                )

    # flags are parsed and passed to the assigned function like so:
    # *args catches all uncaught command arguments as an array.
    def some_func(self, message, *args, output="output", force=False, quiet=False):
        self.bot.msg(
            message.target,
            "You probably meant to use one of the commands. Try $cookie help",
        )

    def balance(self, message):
        # sends a message to the channel it came from
        cookies = self.db.find_one({"user": message.author})
        if not cookies:
            self.bot.msg(message.target, "You have no cookies :(")
        else:
            self.bot.msg(
                message.target,
                "You have %s cookie%s!"
                % (cookies["cookies"], "s" if cookies["cookies"] > 1 else ""),
            )

    def summon(self, message):
        if message.author == 200329561437765652:
            self.bot.msg(
                message.target,
                "A cookie appeared",
                reactions=(("🍪", self.collect_cookie),),
                delete_after=60,
            )
        else:
            self.bot.msg(message.target, "You can't do that!")

    def collect_cookie(self, r):
        if r["reactor"] == self.bot.server.me():
            return
        self.bot.msg(
            r["channel"], "Cookie collected by <@%s>" % r["reactor"], delete_after=60
        )
        del self.bot.server.reaction_callbacks[r["message"]]
        if not self.db.find_one({"user": r["reactor"]}):
            self.db.insert_one({"user": r["reactor"], "cookies": 1})
        else:
            self.db.update({"user": r["reactor"]}, {"$inc": {"cookies": 1}})
