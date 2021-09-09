from taiiwobot import Plugin
import dateparser
import time
from datetime import datetime


class Countdown(Plugin):
    def __init__(self, bot):
        self.bot = bot
        self.interface = bot.util.Interface(
            "countdown",  # plugin name
            "Set a countdown until/for a time. Args: time/date parsible string",  # plugin description
            [  # Flags: <short form> <long form> <description> <1=string or 0=bool>
                # these will be loaded as kwargs to your main function
                "p ping A message to say when the countdown is complete 1"
            ],
            self.countdown,  # main function
            subcommands=[],
        ).listen()  # sets the on message callbacks and parses messages

    def count_thread(self, timeobj, message, target):
        time.sleep(timeobj.timestamp() - time.time())
        self.bot.msg(target, message, follows=message)

    def countdown(self, message, *time_words, ping="Time's up"):
        timeobj = dateparser.parse(
            " ".join(time_words), settings={"PREFER_DATES_FROM": "future"}
        )
        self.bot.util.thread(self.count_thread, (timeobj, ping, message.target))
        if time.time() > timeobj.timestamp():
            self.bot.msg(
                message.target,
                "Error, That time is in the past: %s"
                % datetime.fromtimestamp(int(timeobj.timestamp())),
                follows=message
            )
            return
        self.bot.msg(
            message.target,
            "Ok, the timer will finish at %s"
            % (datetime.fromtimestamp(int(timeobj.timestamp()))),
            follows=message
        )
