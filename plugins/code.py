import json
import re
import urllib

import requests
from bs4 import BeautifulSoup
from taiiwobot.plugin import Plugin


class Code(Plugin):
    def __init__(self, bot):
        self.bot = bot
        self.interface = bot.util.Interface(
            "code",
            "This plugin runs code in a large variety of languages. Args: [language] [args\\n] <code/codeblock> [stdin]",
            [],
            self.run,
            subcommands=[
                bot.util.Subcommand(
                    "man",
                    "Gets linux manpages from man.cs. Args: <query>",
                    [],
                    self.man,
                )
            ],
        ).listen()

        self.versions = json.loads(
            requests.get("https://emkc.org/api/v1/piston/versions").text
        )
        self.languages = []
        for l in self.versions:
            self.languages += l["aliases"]
        self.languages.append("python")

        @bot.on("message", self.name)
        def look_for_codeblocks(message):
            m = re.match(r"```(\w+)\n.*```", message.content, flags=re.DOTALL)
            if (
                message.author == self.bot.server.me()
                or not m
                or m.group(1) not in self.languages
            ):
                return
            if message.raw_message.reactions:
                for r in message.raw_message.reactions:
                    if r.emoji == "🏃" and r.count >= 2:
                        self.bot.server.trigger("reaction", r, r.message.author)
            else:
                emoji = "🏃"
                print(emoji)
                self.bot.server.add_reaction(emoji, message)

        @bot.on("reaction", self.name)
        def run_code(reaction, reactor):
            if (
                reaction.emoji != "🏃"
                or reactor.id == self.bot.server.me()
                or reaction.count != 2
            ):
                return
            message = self.bot.server.format_message(reaction.message)
            m = re.match(r"```(\w+)\n(.*)```", message.content, flags=re.DOTALL)
            if not m:
                raise self.bot.util.RuntimeError(
                    "Not a valid codeblock", message.target, self
                )
            lang = m.group(1)
            code = m.group(2)
            r = self.execute_code(lang, code, "", [])
            if r["stderr"]:
                lang = lang + "\n"
            else:
                lang = ""
            if r["output"].count("\n") > 40 or len(r["output"]) > 1990:
                raise self.bot.util.RuntimeError(
                    "Code output too long!", message.target, self
                )
            if not r["output"]:
                raise self.bot.util.RuntimeError(
                    "Code returned nothing.", message.target, self
                )
            self.bot.msg(
                message.target,
                self.bot.server.code_block(lang + r["output"]),
                follows=message,
            )

    def parse_input(self, message):
        m = re.match(
            r"[^\s]+ *(\w*)(?:\n*([^\n]*)\n?```(\w*)\n?(.*)```\s*(.*))?\s*(.*)",
            message.content,
            flags=re.DOTALL,
        )
        if not m:
            raise self.bot.util.RuntimeError(
                "Invalid syntax, see help info", message.target, self
            )
        if m.group(6):
            lang = m.group(1)
            code = m.group(6).strip("`")
            stdin = ""
            args = []
        else:
            lang = m.group(1) or m.group(3)
            code = m.group(4)
            stdin = m.group(5)
            args = m.group(2).split()
        return lang, code, stdin, args

    def run(self, message, *args):
        lang, code, stdin, args = self.parse_input(message)
        r = self.execute_code(lang, code, stdin, args)
        if r["stderr"]:
            lang = lang + "\n"
        else:
            lang = ""
        if r["output"].count("\n") > 40 or len(r["output"]) > 1990:
            raise self.bot.util.RuntimeError(
                "Code output too long! Must be under 200 characters or 40 lines.",
                message.target,
                self,
            )
        if not r["output"]:
            raise self.bot.util.RuntimeError(
                "Code returned nothing.", message.target, self
            )
        self.bot.msg(
            message.target,
            self.bot.server.code_block(lang + r["output"]),
            follows=message,
        )

    def execute_code(self, lang, code, stdin, args):
        r = requests.post(
            "https://emkc.org/api/v1/piston/execute",
            {"language": lang, "source": code, "stdin": stdin, "args": args},
        )
        output = json.loads(r.text)
        output["output"] = output["output"].replace("```", "``­`­")
        return output

    def man(self, message, *query):
        query = " ".join(query)
        base_url = f"https://man.cx/{query}"
        url = urllib.parse.quote_plus(base_url, safe=";/?:@&=$,><-[]")
        r = requests.get(url)
        if r.status != 200:
            raise self.bot.util.RuntimeError(
                "Error connecting to API", message.target, self
            )
        soup = BeautifulSoup(r.text, "lxml")
        name_tag = soup.find("h2", string="NAME\n")
        if not name_tag:
            raise self.bot.util.RuntimeError(
                f"No manual entry for {query}", message.target, self
            )
        # Get the two (or less) first parts from the nav aside
        # The first one is NAME, we already have it in nameTag
        contents = soup.find_all("nav", limit=2)[1].find_all("li", limit=3)[1:]
        if contents[-1].string == "COMMENTS":
            contents.remove(-1)
        title = name_tag.text
        self.bot.msg(message.target, self.bot.server.code_block(contents))
