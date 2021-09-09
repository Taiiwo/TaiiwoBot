import json
from . import irc


class Config(dict):
    def __init__(self, config_location="config.json", key=False):
        self.config_location = config_location
        self.key = key
        default_config = {
            "irc_config": {
                "type": "irc",
                "host": "example.com",
                "user": "TaiiwoBot",
                "nick": "TaiiwoBot",
                "ident": "TaiiwoBot",
                "autojoin": [],
            },
            "discord_config": {
                "owner[REMOVE]": "your user ID",
                "api_key[REMOVE]": "Insert your api key here and remove the [REMOVE] tag from the key <--",
            },
            "test_config": {},
        }
        try:
            user_config = json.loads(open(config_location).read())
        except (IOError, OSError):
            answer = input(
                "No config file was found. Would you like to generate one? (y/N)"
            )
            if answer[0].lower() == "y":
                open(config_location, "w+").write(
                    json.dumps(default_config, indent=4, separators=(",", ": "))
                )
                print("[i] A config file was created. Edit it and try again")
            else:
                print("[i] A config file is required to run TaiiwoBot")
            quit()
        default_config[key].update(user_config)
        for k, v in default_config[key].items():
                super().__setitem__(k, v)

    def save_config(self):
        with open(self.config_location, "w") as f:
            f.write(json.dumps(self, indent=4))
