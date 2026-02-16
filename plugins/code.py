import json
import re
import urllib

import requests
from bs4 import BeautifulSoup
from taiiwobot.plugin import Plugin
import piston_rspy


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

        self.client = piston_rspy.Client().with_url("https://emkc.org/api/v2/piston")
        with open("./lib/cicada/cicada/gematria.py") as f:
            self.gematria = piston_rspy.File(
                name="cicada/gematria.py",
                content=f.read(),
            )
        with open("./lib/cicada/cicada/liberprimus.py") as f:
            self.liberprimus = piston_rspy.File(
                name="cicada/liberprimus.py",
                content=f.read(),
            )

        with open("./lib/cicada/cicada/liber_primus.txt") as f:
            self.liberprimus_text = piston_rspy.File(
                name="cicada/liber_primus.txt",
                content=f.read(),
            )

        self.cicada_init = piston_rspy.File(
            name="cicada/__init__.py",
            content="from .gematria import Runes, Latin\nfrom .liberprimus import LiberPrimus\n",
        )

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
                        self.bot.server.trigger(
                            "reaction", r, r.message.author)
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
            m = re.match(r"```(\w+)\n(.*)```",
                         message.content, flags=re.DOTALL)
            if not m:
                raise self.bot.util.RuntimeError(
                    "Not a valid codeblock", message.target, self
                )
            lang = m.group(1)
            code = m.group(2)
            self.execute_code(lang, code, "", [], message)

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
        r = self.execute_code(lang, code, stdin, args, message)

    def execute_code(self, lang, code, stdin, args, message):

        async def f(lang, code, stdin, args, message):
            if lang == "python":
                code = "from cicada import Runes, Latin, LiberPrimus\nlp = LiberPrimus()\n" + \
                    code
                r = await self.client.execute(
                    piston_rspy.Executor()
                    .set_language("python")
                    .add_files([
                        piston_rspy.File(name="main.py", content=code),
                        self.gematria, self.liberprimus_text, self.liberprimus, self.cicada_init
                    ])
                )
                r = r.run
                output, stderr = r.output, r.stderr
            else:
                r = requests.post(
                    "https://emkc.org/api/v1/piston/execute",
                    {"language": lang, "source": code,
                        "stdin": stdin, "args": args},
                )
                r = json.loads(r.text)
                output, stderr = r["output"], r["stderr"]

            output = output.replace("```", "``­`­")
            if stderr:
                lang = lang + "\n"
            else:
                lang = ""
            if output.count("\n") > 40 or len(output) > 1990:
                print(output)
                raise self.bot.util.RuntimeError(
                    "Code output too long! Must be under 2000 characters or 40 lines.",
                    message.target,
                    self,
                )
            if not output:
                raise self.bot.util.RuntimeError(
                    "Code returned nothing.", message.target, self
                )
            self.bot.msg(
                message.target,
                self.bot.server.code_block(lang + output),
                follows=message,
            )
        self.bot.server.gaysyncio([
            [f, (lang, code, stdin, args, message), {}],
        ])

    def man(self, message, *query):
        query = " ".join(query)
        base_url = f"https://man.cx/{query}"
        url = urllib.parse.quote_plus(base_url, safe=";/?:@&=$,><-[]")
        r = requests.get(url)
        if r.status_code != 200:
            raise self.bot.util.RuntimeError(
                "Error connecting to API", message.target, self
            )
        # parse as xml
        soup = BeautifulSoup(r.text, "html.parser")
        # get the first
        name_tag = soup.find("h2", string="NAME\n")
        # get the last h2 on the page
        if not name_tag:
            raise self.bot.util.RuntimeError(
                f"No manual entry for {query}", message.target, self
            )
        last_tag = soup.find_all("h2")[-1]
        response = ""
        # for each h2 tag as title
        tag = name_tag
        while tag != last_tag:
            if tag.name == "h2":
                response += f"**{tag.text}**\n"
            elif tag.name == "p":
                # get the text
                text = tag.get_text().replace("\n", " ")
                # add the text to the response
                response += text + "\n\n"
            elif tag.name == "table":
                # for each row in the table
                for row in tag.find_all("tr"):
                    # add the cells to the response
                    response += row.get_text().replace("\n", " ") + "\n"
                response += "\n"
            tag = tag.find_next_sibling()
        self.bot.msg(message.target, response[:2000], follows=message)
