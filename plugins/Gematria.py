from taiiwobot.plugin import Plugin
import math

import lib.cicada.cicada
from lib.cicada.cicada.gematria import Latin, Runes

cicada = lib.cicada.cicada


class Gematria(Plugin):
    def __init__(self, bot):
        self.bot = bot
        self.lp = cicada.LiberPrimus()
        self.interface = bot.util.Interface(
            "gp",  # command name
            # plugin description
            "translates runes and latin using the Gematria Primus.",
            [  # Flags: "<short form> <long form> <description> <1=string or 0=bool>"
                # "o output Specifies the location of the output file 1",
            ],
            self.main,  # root function
            subcommands=[  # list of subcommands
                bot.util.Interface(
                    "runes",  # invoked with $template sub <args/flags>
                    "Translates string to runes Args: <string>",  # subcommand description
                    [
                        "a atbash Perform atbash 0",
                    ],  # subcommand flags
                    self.runes,  # subcommand function
                ),
                bot.util.Interface(
                    "latin",  # invoked with $template sub <args/flags>
                    "Translates string to latin Args: <string>",  # subcommand description
                    [
                        "a atbash Perform atbash 0",
                    ],  # subcommand flags
                    self.latin,  # subcommand function
                ),
                bot.util.Interface(
                    "sum",  # invoked with $template sub <args/flags>
                    "Returns the gematria sum for a string: <string>",  # subcommand description
                    [
                        "r runic Supply input in runes instead of latin 0",
                    ],  # subcommand flags
                    self.sum,  # subcommand function
                ),
                bot.util.Interface(
                    "sum_index",  # invoked with $template sub <args/flags>
                    "Returns the sum of indexes for a string: <string>",  # subcommand description
                    [
                        "r runic Supply input in runes instead of latin 0",
                    ],  # subcommand flags
                    self.sum_index,  # subcommand function
                ),
            ],
        ).listen()  # sets the on message callbacks and parses messages

    def main(self, message, *args):  # include your root flags here
        self.interface.help(message.target, self)

    def runes(self, message, *args, numeric=False, atbash=False):
        string = " ".join(args)
        input = Latin(string)

        if atbash:
            alpha = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
            runes = input.to_runes().substitute(alpha, alpha[::-1])
        else:
            runes = input.to_runes().text
        self.bot.msg(message.target, self.bot.server.code_block(runes), follows=message)

    def latin(self, message, *args, numeric=False, atbash=False):
        string = " ".join(args)
        input = Runes(string)

        if atbash:
            alpha = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
            latin = Runes(input.substitute(alpha, alpha[::-1])).to_latin().text
        else:
            latin = input.to_latin().text
        self.bot.msg(message.target, self.bot.server.code_block(latin), follows=message)

    def sum(self, message, *args, runes=False):
        if runes:
            input = Runes(" ".join(args))
        else:
            input = Latin(" ".join(args))
        n = input.gematria_sum()
        self.bot.msg(message.target, n, follows=message)
        if n not in [0, 1] and all(n % p != 0 for p in range(2, int(math.sqrt(n)) + 1)):
            self.bot.msg(message.target, "It's also prime!", follows=message)
            n = int(str(n)[::-1])
            if all(n % p != 0 for p in range(2, int(math.sqrt(n)) + 1)):
                self.bot.msg(message.target, "!emirp osla s'tI", follows=message)

    def sum_index(self, message, *args, runes=False):
        if runes:
            input = Runes(" ".join(args))
        else:
            input = Latin(" ".join(args))
        n = sum(input.to_runes().to_index())
        self.bot.msg(message.target, n, follows=message)
        if n not in [0, 1] and all(n % p != 0 for p in range(2, int(math.sqrt(n)) + 1)):
            self.bot.msg(message.target, "It's also prime!", follows=message)
            n = int(str(n)[::-1])
            if all(n % p != 0 for p in range(2, int(math.sqrt(n)) + 1)):
                self.bot.msg(message.target, "!emirp osla s'tI", follows=message)
