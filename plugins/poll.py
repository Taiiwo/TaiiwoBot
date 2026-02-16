from taiiwobot.plugin import Plugin


class Poll(Plugin):
    def __init__(self, bot):
        self.bot = bot
        self.interface = bot.util.Interface(
            "poll",
            "Create a poll",
            [
                "p prompt The prompt for the poll 1",
                "o options The options for the poll, separated by commas 1",
                "e emojis The emojis to use for the poll 1"
            ],
            self.create_poll,
            subcommands=[
                bot.util.Subcommand(
                    "create",
                    "Create a new poll",
                    [
                        "p prompt The prompt for the poll 1",
                        "o options The options for the poll, separated by commas 1",
                        "e emojis The emojis to use for the poll 1"
                    ],
                    self.create_poll
                )
            ]
        ).listen()

    def create_poll(self, message, *args, prompt="", options=None, emojis=False):
        if options is None:
            options = ["yes", "no"]
        else:
            options = options.split(",")

        if emojis:
            answers = [[emojis[i % len(emojis)], option, lambda x: False]
                       for i, option in enumerate(options)]
        else:
            answers = [[option, lambda x: False] for option in options]

        self.bot.menu(message.target, None, prompt,
                      answers=answers)
