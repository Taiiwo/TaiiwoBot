from taiiwobot.plugin import Plugin

import requests
import json


class CicadaWiki(Plugin):
    def __init__(self, bot):
        self.bot = bot
        self.interface = bot.util.Interface(
            "uc",  # command name
            # plugin description
            "Searches a query on the UncoveringCicada wiki.",
            [  # Flags: "<short form> <long form> <description> <1=string or 0=bool>"
                # "o output Specifies the location of the output file 1",
            ],
            self.main,  # root function
            subcommands=[],
        ).listen()  # sets the on message callbacks and parses messages

    def main(self, message, *args):  # include your root flags here
        query = "%20".join(args)
        wikiajson = r = requests.get("http://uncovering-cicada.wikia.com/api.php", params={
            "action":"query",
            "list":"search",
            "srsearch": " ".join(args),
            "utf8": True,
            "format":"json"
        }).text
        wikiaobj = json.loads(wikiajson)
        if len(wikiaobj["query"]["search"]) == 0:
            self.bot.msg(message.target, "No results.", follows=message)
            return
        article = wikiaobj["query"]["search"][0]
        url = "https://uncovering-cicada.fandom.com/wiki/" + article["title"].replace(" ", "_")
        self.bot.msg(message.target, article["title"] + " - " + url, follows=message)
