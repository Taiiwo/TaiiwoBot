from taiiwobot import Plugin


class CicadaLinks(Plugin):
    def __init__(self, bot):
        self.bot = bot

        self.links = {
            "pages": "https://www.dropbox.com/sh/lkta4q921vliyuw/AADmZ1YUHXWSjSizlMGZHXVMa?dl=0",
            "transcript": "https://github.com/rtkd/iddqd/blob/master/liber-primus__transcription--master/liber-primus__transcription--master.txt",
            # "wekan": "https://3301.ga/wekan/",
            "reddit": "https://www.reddit.com/r/CicadaSolvers/",
            "wiki": "https://uncovering-cicada.fandom.com/wiki/Uncovering_Cicada_Wiki",
        }

        self.interface = bot.util.Interface(
            "link",
            "Provides various helpful links.",  # plugin description
            [],
            self.list,  # main function
            subcommands=[],
        ).listen()  # sets the on message callbacks and parses messages

    # flags are parsed and passed to the assigned function like so:
    # *args catches all uncaught command arguments as an array.
    def list(self, message, *args):
        if len(args) == 0:
            links = "\n".join(
                ["%s - %s" % (link, self.links[link]) for link in self.links]
            )
            self.bot.msg(
                message.target,
                "Here is a list of all supported links: \n ```%s```" % links,
                follows=message
            )
        elif args[0] in self.links:
            self.bot.msg(message.target, self.links[args[0]], follows=message)
        else:
            self.bot.msg(message.target, "Invalid link name!", follows=message)
