from taiiwobot.plugin import Plugin
import requests
import json
from datetime import datetime


class LastFm(Plugin):
    def __init__(self, bot):
        self.bot = bot
        if not "lastfm_key" in self.bot.config:
            print(
                'Last.FM API Keys not specified. Add `"lastfm_key": "<your key>",` to your config file.'
            )
            return None
        self.interface = bot.util.Interface(
            "fm",
            "Last.FM command for displaying your now playing and other features",
            ["r rhythm Command rhythm to play your now playing song 0"],
            self.fm,
            subcommands=[
                bot.util.Subcommand(
                    "link",
                    "Links your last.fm account to your discord account",
                    [],
                    self.link,
                ),
                bot.util.Subcommand(
                    "profile", "Displays your Last.FM profile", [], self.profile,
                ),
                bot.util.Subcommand(
                    "yt",
                    "Posts a youtube link for your nowplaying song or query. Args: [keywords]",
                    [],
                    self.fmyt,
                ),
            ],
        ).listen()
        self.api_url = "http://ws.audioscrobbler.com/2.0/"

        self.api_key = self.bot.config["lastfm_key"]
        self.youtube_key = self.bot.config["youtube_key"]
        self.db = self.bot.util.get_db()["lastfm"]
        # self.bot.config["lastfm"]["api_secret"]
        lastfm = self

        class NotRegistered(self.bot.util.RuntimeError):
            def __init__(self, target):
                super().__init__(
                    "You've not linked your last.fm account yet. Use $fm link",
                    target,
                    lastfm,
                )

        self.NotRegistered = NotRegistered

        class UserNotFound(self.bot.util.RuntimeError):
            def __init__(self, target):
                super().__init__(
                    "The linked last.fm account is not valid. Use $fm link",
                    target,
                    lastfm,
                )

        self.UserNotFound = UserNotFound

    def get_youtube(self, query):
        search = json.loads(
            requests.get(
                "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&q=%s&key=%s"
                % (query, self.youtube_key)
            ).text
        )
        if not "items" in search:
            return search["error"]["message"]
        for item in search["items"]:
            if "videoId" in item["id"]:
                video_id = item["id"]["videoId"]
                return "https://youtube.com/watch?v=" + video_id
        return "No results"

    def fmyt(self, message, *keywords):
        if len(keywords) > 0:
            track_name = " ".join(keywords)
        else:
            user = self.get_user(message)
            track = self.get_nowplaying(user)
            track_name = track["name"]
        self.bot.msg(message.target, self.get_youtube(track_name), follows=message)

    def get_nowplaying(self, user):
        if not user:
            raise self.NotRegistered(message.target)
        recents = json.loads(
            requests.get(
                self.api_url
                + "?method=user.getrecenttracks&user=%s&api_key=%s&format=json&limit=1"
                % (user["lastfm_user"], self.api_key)
            ).text
        )
        return recents["recenttracks"]["track"][0]

    def fm(self, message, rhythm=False):
        user = self.get_user(message)
        track = self.get_nowplaying(user)
        self.bot.msg(
            message.target,
            "Now Playing:",
            embed=self.bot.server.embed(
                title=track["name"],
                url=self.get_youtube(track["name"]),
                desc=track["album"]["#text"],
                author_name=track["artist"]["#text"],
                thumbnail=track["image"][-1]["#text"],
            ),
            follows=message,
        )

    def link(self, message, username, *args):
        current_user = self.db.find_one({"discord_id": message.author})
        if current_user:
            self.db.update(
                {"discord_id": message.author}, {"$set": {"lastfm_user": username}}
            )
        else:
            self.db.insert_one({"discord_id": message.author, "lastfm_user": username})
        self.bot.msg(message.target, "Account linked successfully!", follows=message)

    def get_user(self, message):
        user = self.db.find_one({"discord_id": message.author})
        if user:
            return user
        else:
            raise self.NotRegistered(message.target)

    def profile(self, message, username=False):
        if not username:
            username = self.get_user(message)["lastfm_user"]
        user_info = json.loads(
            requests.get(
                self.api_url
                + "?method=user.getinfo&user=%s&api_key=%s&format=json"
                % (username, self.api_key)
            ).text
        )["user"]
        self.bot.msg(
            message.target,
            " ",
            embed=self.bot.server.embed(
                title=user_info["name"],
                url=user_info["url"],
                thumbnail=user_info["image"][-1]["#text"],
                fields=[
                    ["age", user_info["age"]],
                    ["gender", user_info["gender"]],
                    ["country", user_info["country"]],
                    ["playcount", user_info["playcount"]],
                    [
                        "registered",
                        datetime.fromtimestamp(
                            int(user_info["registered"]["unixtime"])
                        ),
                    ],
                    ["playlists", user_info["playlists"]],
                    ["subscribers", user_info["subscriber"]],
                    ["bootstrap", user_info["bootstrap"]],
                ],
            ),
            follows=message,
        )
