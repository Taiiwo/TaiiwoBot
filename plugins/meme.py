from taiiwobot import Plugin
import requests
import json


class Meme(Plugin):
    def __init__(self, bot):
        self.bot = bot

        self.templates = {
            "drake": "181913649",
            "buttons": "87743020",
            "changemymind": "129242436",
            "nut": "119139145",
            "smart": "89370399",
            "pikachu": "155067746",
            "doge": "8072285",
            "butterfly": "100777631",
            "rock": "21735",
            "harold": "27813981",
            "skeptical": "101288",
            "allthethings": "61533",
            "smugsponge": "101511",
            "success": "61544",
            "pills": "132769734",
            "unclesam": "89655",
            "aliens": "101470",
            "trump": "91545132",
            "smudge": "188390779",
            "ascended": "93895088",
        }

        self.interface = bot.util.Interface(
            "meme",  # plugin name
            # plugin description
            "Makes memes using templates. Meme text is newline delimited Usage: $meme <template> <text>",
            [],
            self.meme,  # main function
            subcommands=[
                self.bot.util.Subcommand(
                    "templates",
                    "Lists available meme templates",
                    [],
                    self.list_templates,
                )
            ],
        ).listen()  # sets the on message callbacks and parses messages

    # flags are parsed and passed to the assigned function like so:
    # *args catches all uncaught command arguments as an array.
    def meme(self, message, *args):
        args = message.content.splitlines()
        args[0] = " ".join(args[0].split()[1:])
        print(args)
        if args[0] in self.templates:
            args[0] = self.templates[args[0]]
        else:
            search = json.loads(requests.get(
                "https://imgflip.com/ajax_meme_search_new?q=%s&transparent_only=0&include_nsfw=1&allow_gifs=0" % (
                    args[0]
                )
            ).text)["results"]
            if len(search) > 0:
                args[0] = search[0]["id"]
            else:
                return self.bot.msg(message.target, "Invalid ID or search returned nothing", follows=message)
        text = args[1:]
        text.extend([""] * (4 - len(text)))
        data = {
            "template_id": args[0],
            "username": "taiiwobot",
            "password": "taiiwobot",
            "text0": text[0],
            "text1": text[1],
        }
        data.update({"boxes[%s][text]" % i: t for i, t in enumerate(text)})
        res = requests.post(
            "https://api.imgflip.com/caption_image", data=data,)
        res = json.loads(res.text)
        if res["success"]:
            self.bot.msg(message.target, res["data"]["url"], follows=message)
        else:
            self.bot.msg(message.target, res["error_message"], follows=message)

    def list_templates(self, message, *args):
        self.bot.msg(
            message.target,
            "Meme ids can be found here: https://api.imgflip.com/popular_meme_ids. You can also use the following aliases: %s"
            % (", ".join(self.templates.keys())), follows=message
        )
