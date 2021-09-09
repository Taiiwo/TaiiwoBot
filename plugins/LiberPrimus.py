from taiiwobot.plugin import Plugin

import lib.cicada.cicada

cicada = lib.cicada.cicada
Gematria = cicada.gematria.Gematria


class LiberPrimus(Plugin):
    def __init__(self, bot):
        self.bot = bot
        self.lp = cicada.LiberPrimus()
        self.interface = bot.util.Interface(
            "lp",  # command name
            # plugin description
            "Retrieves and translates pages of the Liber Primus. Args: <page_number>",
            [  # Flags: "<short form> <long form> <description> <1=string or 0=bool>"
                "l latin returns the page in latin form 0",
                "n number returns the page in number form 0",
                "p part Select part 1 or 2 1",
                "i image Returns page image instead 0",
            ],
            self.page,  # root function
            subcommands=[  # list of subcommands
                bot.util.Interface(
                    "page",  # invoked with $template sub <args/flags>
                    "Retrieves and translates pages of the Liber Primus. Args: <page_number>",
                    [
                        "l latin returns the page in latin form 0",
                        "n number returns the page in number form 0",
                        "p part Select part 1 or 2 1",
                        "i image Returns page image instead 0",
                    ],  # subcommand flags
                    self.page,  # subcommand function
                )
            ],
        ).listen()  # sets the on message callbacks and parses messages

    def main(self, message, *args):  # include your root flags here
        self.interface.help(message.target, self)

    def page(
        self,
        message,
        page_number,
        *args,
        latin=False,
        number=False,
        part="2",
        image=False
    ):
        if part.isnumeric():
            part = int(part)
        else:
            raise self.bot.util.RuntimeError(
                "Invalid part number", message.target, self
            )
        if page_number.isnumeric():
            page_number = int(page_number)
        else:
            raise self.bot.util.RuntimeError(
                "Invalid page number", message.target, self
            )
        if (
            page_number < 0
            or (page_number > 16 and part == 1)
            or (page_number > 57 and part == 2)
        ):
            print(page_number)
            raise self.bot.util.RuntimeError(
                "Invalid page number", message.target, self
            )
        if image:
            if part == 1:
                if page_number == 1:
                    page_number = 2
                elif page_number == 2:
                    page_number = 1
                elif page_number == 3:
                    page_number = 4
                elif page_number == 4:
                    page_number = 5
                elif page_number == 5:
                    page_number = 3
                self.bot.msg(
                    message.target,
                    "https://opensource.cicada.gq/images/LP1_%s.jpg" % (page_number),
                    follows=message,
                )
            else:
                self.bot.msg(
                    message.target,
                    "https://opensource.cicada.gq/images/%s.jpg" % (page_number),
                    follows=message,
                )
            return
        if part == 1 and page_number == 0:
            self.bot.msg(
                message.target,
                self.bot.server.code_block("Liber Primus"),
                follows=message,
            )
            return
        elif part == 1 and page_number == 1:
            page_number = 0
        elif part == 1 and page_number == 2:
            self.bot.msg(
                message.target,
                self.bot.server.code_block("Chapter 1\nIntus"),
                follows=message,
            )
            return
        else:
            page_number -= 2
        page = self.lp.pages[(17 if part == 2 else 0) + int(page_number)]
        if latin:
            page = page.runes.to_latin()
        if number:
            page = page.runes.to_numbers()
        self.bot.msg(
            message.target, self.bot.server.code_block(str(page)), follows=message
        )
