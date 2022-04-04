import re
import json
import discord
import requests
import youtube_dl
import discord.utils
from taiiwobot import Plugin
from discord_components import DiscordComponents, Button, ActionRow, ButtonStyle

class Voice(Plugin):
    def __init__(self, bot):
        self.bot = bot
        self.interface = bot.util.Interface(
            "voice", # plugin name
            "This plugin handles various voice-chat features", [], self.voice,
            subcommands=[
                bot.util.Interface(
                    "play",
                    "plays or unpauses any given audio source; keyword search or URL",
                    [
                        "s search keywords or URL to any audio-source 1",
                        "t target channel to join 1"
                    ],
                    self.play
                ),
               bot.util.Interface(
                    "queue",
                    "Allows queue handling",
                    [],
                    self.__queue,
                    subcommands=[
                        bot.util.Interface(
                            "show", "Shows queue in chat", [], self.show_queue
                        ),
                        bot.util.Interface(
                            "clear", "Clears queue", [], self.clear_queue
                        ),
                        bot.util.Interface(
                            "pop", "Removes item from queue", ['t track_ints to remove from queue (space separated) 1'], self.pop_queue
                        )
                    ]
                ),
                bot.util.Interface(
                    "disconnect", "Disconnects bot from voice", [], self.disconnect
                ),
                bot.util.Interface(
                    "skip", "Skips current playing track for next in queue", [], self.skip_track
                ),
                bot.util.Interface(
                    "pause", "Pauses audio playback", [], self.pause_track
                )
            ]
        ).listen() # Begin listening for messages

        self.channels_ids = []
        self.is_streaming_audio = False
        self.is_paused = False
        self.bot_voice = None
        self.full_search = False
        self.queue = {}
        self.sent_embeds = []
        self.icon_url ='https://media1.giphy.com/media/MZFdCUZBFEn9FnJDrQ/giphy.gif?cid=790b761113f03f5e21dfd642a3ae437808dfe2d3683369a5&rid=giphy.gif&ct=s'

        self.userid_whitelist = []

        self.YT_HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
        self.YT_DL_OPTS = {'format': 'bestaudio', 'quiet': True}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        DiscordComponents(self.bot)

        for channel in self.bot.server.client.get_all_channels():
            self.channels_ids.append(channel.id)

    def voice(self, *args):
        pass

    def __queue(self, *args):
        pass

    def show_queue(self, message):
        embed = discord.Embed(color=self.bot.server.client.user.color)
        embed.set_author(name='Queue', icon_url=self.icon_url)
        embed.set_footer(text='TaiiwoBot')

        if len(self.queue) > 0:
            track_names = list(self.queue.keys())

            for i in range(0, len(track_names)):
                track_name = track_names[i]

                if len(track_name) >= 65:
                    track_name = track_name[0:62].strip()
                    track_name += '...'

                embed.insert_field_at(i, name=f'`song_len_here`', value=f'`{i}` - {track_name}', inline=False)
        else:
            embed.description = '**Empty**'

        self.bot.msg(message.target, message=None, embed=embed)

    def pop_queue(self, message, *args):
        track_ints = list(args)

        if len(track_ints) > 0:
            track_ints = [int(i) for i in track_ints]
            keys_to_remove = []

            for track_int in track_ints:
                if track_int in range(len(self.queue)):
                    keys_to_remove.append(list(self.queue.keys())[track_int])
                else:
                    self.bot.msg(message.target, message='There is no such track in queue.')
                    return

            for key in keys_to_remove:
                self.queue.pop(key)

            self.bot.msg(message.target, message='Popped.')
        else:
            self.bot.msg(message.target, message='You did not specify any tracks.')

    def clear_queue(self, message):
        self.queue.clear()
        self.bot.msg(message.target, message='Queue cleared.')

    def check_queue(self, entry):
        if entry[next(iter(entry))] in self.queue.values():
            # if next song in queue is the song
            # that is playing, just replay it.
            self.queue.pop(entry)
            return 1
        else:
            return 0

    def add_to_queue(self, entry):
        queue_code = 0 or self.check_queue(entry)

        if queue_code == 0:
            self.queue.update(entry)
            queue_code = 0

        return queue_code

    def remove_from_queue(self, value):
        # title = list(self.queue.keys())[[tup[0] for tup in list(self.queue.values())].index(value)]
        title = list(self.queue.keys())[list(self.queue.values()).index(value)]
        self.queue.pop(title)

    def get_queue_next(self):
        return self.queue[next(iter(self.queue))] if len(self.queue) > 0 else None

    def skip_track(self, *args):
        self.bot_voice.stop()

        audio = self.get_queue_next()
        if audio:
            self.remove_from_queue(audio)
            self.__stream(audio)

    def pause_track(self, *args):
        self.is_paused = True
        self.bot_voice.pause()

    def get_status_embed(self, embed_type, track_info):
        embed = discord.Embed(title=track_info['title'], color=self.bot.server.client.user.color)
        embed.set_author(name=embed_type, icon_url=self.icon_url)
        embed.set_thumbnail(url=track_info['thumbnail'])
        # embed.description = track_info['channel']
        embed.set_footer(text='TaiiwoBot') # text=track_info['channel']

        return embed

    def remove_embeds(self):
        async def gaysync():
            for embed in self.sent_embeds:
                await embed.delete()
            self.sent_embeds = []

        self.bot.server.gaysyncio([[gaysync, [], {}]])

    def __stream(self, audio):
        def do_stream_complete(*args):
            self.is_streaming_audio = False

            if len(self.queue) > 0:
                audio = self.get_queue_next()
                self.remove_from_queue(audio)

                self.is_streaming_audio = True
                self.__stream(audio)

        self.is_streaming_audio = True
        try:
            self.bot_voice.play(
                discord.FFmpegPCMAudio(audio, **self.FFMPEG_OPTIONS),
                after=do_stream_complete
            )
        except discord.errors.ClientException:
            return False
        except AttributeError:
            return False

    def stream_to_vc(self, message, target_channel, **kwargs):
        async def gaysync():
            if 'join' in kwargs:
                self.join_vc(target_channel)

            self.play_track(
                message,
                valid_track_url=kwargs['is_valid_track_url'] if 'is_valid_track_url' in kwargs else None,
                valid_youtube_url=kwargs['is_valid_youtube_url'] if 'is_valid_youtube_url' in kwargs else None,
                search_string=kwargs['search_string']
            )

        self.bot.server.gaysyncio([[gaysync, [], {}]])

    def join_vc(self, target_channel):
        async def gaysync():
            if not self.bot_voice:
                voice_channel = self.bot.server.client.get_channel(target_channel) if type(target_channel) == int else target_channel
                self.bot_voice = await voice_channel.channel.connect() # cls=voice_recv.VoiceRecvClient

        self.bot.server.gaysyncio([[gaysync, [], {}]])

    def disconnect(self, message):
        async def gaysync():
            author_vc = message.raw_message.author.voice

            if author_vc == None:
                self.bot.msg(message.target, 'No. You aren\'t in a voice-channel.')

            elif self.bot_voice and author_vc.channel.id != self.bot_voice.channel.id:
                self.bot.msg(message.target, 'I am not in your voice channel.')

            elif self.bot_voice:
                await self.bot_voice.disconnect()
                self.bot_voice = None

                if self.sent_embeds:
                    self.remove_embeds()

            else:
                self.bot.msg(message.target, 'I am not in a voice-channel.')

        self.bot.server.gaysyncio([[gaysync, [], {}]])

    def get_youtube_results(self, search_str):
        response = requests.get('https://www.youtube.com/results', params={'search_query': search_str}, headers=self.YT_HEADERS).text

        unsantized_json = response.split('var ytInitialData = ')[1]
        # unsantized_json = unsantized_json.split(']};</script>')[0] + ']}'.strip()
        sanitized_json = unsantized_json.split(';</script>')[0].strip()
        # with open(r'json.txt', 'w', encoding='utf-8') as f:
        #     f.write(sanitized_json)
        sanitized_json = json.loads(sanitized_json)

        try:
            track_info = sanitized_json['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
        except:
            return None

        track_dict = {}
        iteration = 0

        for key in track_info:
            if 'playlistRenderer' in key:
                # add youtube playlist support to instance queue
                pass

            elif 'videoRenderer' in key:
                info = key['videoRenderer']

                try:
                    if info['badges'][0]['metadataBadgeRenderer']['style'] == 'BADGE_STYLE_TYPE_LIVE_NOW':
                        # FOR NOW skip videos that are live, youtube_dl breaks with these results half of the time.
                        continue
                except:
                    pass

                try:
                    track_url = f'https://www.youtube.com/watch?v={info["videoId"]}'
                    track_title = info['title']['runs'][0]['text']

                    thumbnail_url = info['thumbnail']['thumbnails'][0]['url']
                    channel_name = info['longBylineText']['runs'][0]['text']
                    publish_time = info['publishedTimeText']['simpleText']
                    length_time = info['lengthText']['simpleText']
                except KeyError:
                    continue

                track_dict[track_url] = {
                    'title': track_title,
                    'thumbnail': thumbnail_url,
                    'channel': channel_name,
                    'publish_time': publish_time,
                    'length': length_time
                }

                iteration += 1

            if iteration == 3:
                break

        return track_dict

    async def get_youtube_choice(self, message, track_dict):
        async def callback(message):
            self.sent_embeds.append(message)

        tracks = list(track_dict)
        button_colors = [discord.Color.green(), discord.Color.red(), discord.Color.blurple()]
        components = None

        for track in tracks:
            track_number = tracks.index(track)

            choice_embed = discord.Embed(title=f'{track_number + 1}.', color=self.bot.server.client.user.color)
            choice_embed.set_author(name='YouTube')

            curr_track = track_dict[track]

            choice_embed.color = button_colors[track_number]
            choice_embed.add_field(name=curr_track['title'], value=track)
            choice_embed.set_footer(text=f"{curr_track['channel']}\n{curr_track['publish_time']}")
            choice_embed.set_image(url=curr_track['thumbnail'])

            if track_number == 2:
                buttons = [
                    Button(style=ButtonStyle.green, label='Choose Track 1', custom_id=tracks[0]), # style=randint(1, 4) for random color
                    Button(style=ButtonStyle.red, label='Choose Track 2', custom_id=tracks[1]),
                    Button(style=ButtonStyle.blue, label='Choose Track 3', custom_id=tracks[2])
                ]

                components = [ActionRow(*buttons)]

            self.bot.msg(message.target, message=None, embed=choice_embed, components=components, delete_after=15, callback=[callback, ("$0",), {}])

        clicked_button = await self.bot.server.client.wait_for('button_click', timeout=15) # gaysync this shit

        if clicked_button[0].user.id != message.author:
            await clicked_button[0].defer(5, content='You are not the author.')
            pass

        else:
            await clicked_button[0].defer(6)

            self.remove_embeds()
            return clicked_button[1].custom_id

    def get_youtube_info(self, url):
        with youtube_dl.YoutubeDL(self.YT_DL_OPTS) as ydl:
            #FIXME: youtube_dl.utils.DownloadError: ERROR: Sign in to confirm your age This video may be inappropriate for some users.
            info = ydl.extract_info(url, download=False)

            streamable_media = info['formats'][0]['url']
            title = info['title']

            return streamable_media, title

    def play_track(self, message, **kwargs):
        async def gaysync():
            if 'streamable_media' in kwargs:
                success = self.__stream(kwargs['streamable_media'])
                if not success:
                    self.stream_to_vc(message, message.raw_message.channel.id, join=True)
                    self.__stream(kwargs['streamable_media'])
                return

            search_string = kwargs['search_string']
            is_valid_track_url = kwargs['is_valid_track_url'] if 'is_valid_track_url' in kwargs else None
            is_valid_youtube_url = kwargs['is_valid_youtube_url'] if 'is_valid_youtube_url' in kwargs else None

            streamable_media = None
            url_cache = None
            title = None

            if is_valid_track_url:
                if is_valid_youtube_url:
                    streamable_media, title = self.get_youtube_info(is_valid_youtube_url.string)

                else:
                    title = is_valid_track_url.string
                    streamable_media = is_valid_track_url.string
            else:
                track_dict = self.get_youtube_results(search_string)

                if track_dict == None:
                    return

                if self.full_search:
                    streamable_media = await self.get_youtube_choice(message, track_dict)
                    url_cache = streamable_media

                    if streamable_media == 0:
                        return

                    if streamable_media == None:
                        self.bot.msg(message.target, 'No results found.')
                        return

                    self.full_search = False
                else:
                    streamable_media = next(iter(track_dict))
                    url_cache = streamable_media
                streamable_media, title = self.get_youtube_info(streamable_media)

            if self.is_streaming_audio:
                queue_entry = {title: streamable_media}
                queue_code = self.add_to_queue(queue_entry)

                if queue_code == 0:
                    embed = self.get_status_embed('Queued', track_dict[url_cache])
                    self.bot.msg(message.target, message=None, embed=embed)
                    return

                elif queue_code == 1:
                    self.play(None, None, streamable_media=streamable_media)
                    return

            embed = self.get_status_embed('Now Playing', track_dict[url_cache]) # this needs to be sent every time someone skips a song or something also
            self.bot.msg(message.target, message=None, embed=embed)
            self.__stream(streamable_media)

        self.bot.server.gaysyncio([[gaysync, [], {}]])

    def play(self, message, *args, search=None, target=None):
        if not args and self.is_paused:
            self.bot_voice.resume()
            return

        elif not args and not search:
            return

        search_string = search
        is_valid_track_url = None
        is_valid_youtube_url = None

        if search_string:
            self.full_search = True

            if len(args) > 0:
                search_string = f'{search_string} {" ".join(args)}'
        else:
            url_pattern = '(?:(?:https?):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+'
            youtube_pattern = '(https?://)?(www\.)?youtube\.(com|nl)/watch\?v=([-\w]+)'

            track_url = args[0]

            is_valid_track_url = re.match(url_pattern, track_url)
            is_valid_youtube_url = re.match(youtube_pattern, track_url)

            if not is_valid_track_url and not is_valid_youtube_url:
                search_string = ' '.join(args)

        target_channel = None
        author_voice = message.raw_message.author.voice
        author_id = message.raw_message.author.id
        target_channel = author_voice.channel.id if author_voice else target if target else None

        if target:
            target_channel = int(target)
            if target not in self.channel_ids:
                self.bot.msg(message.target, 'I can\'t find that channel.')
                return

            elif target in self.channels_ids and author_id in self.userid_whitelist:
                target_channel = target

            elif target in self.channel_ids and author_id not in self.userid_whitelist:
                self.bot.msg(message.target, 'You do not have permission to target channels.')
        else:
            if author_voice:
                target_channel = author_voice
            else:
                self.bot.msg(message.target, 'You aren\'t in a voice-channel and no target specified.')
                return

        admin = True if author_id in self.userid_whitelist else False

        if not author_voice and admin:
            self.bot.msg(message.target, 'No voice-channel specified.')
            return
        elif not author_voice and not admin:
            self.bot.msg(message.target, 'You are not in a voice-channel.')
            return

        if self.bot_voice and author_voice and author_voice.channel.id != self.bot_voice.channel.id:
            self.bot.msg(message.target, 'I am not in your voice channel.')
            return

        elif self.bot_voice and not author_voice:
            self.bot.msg(message.target, 'No. You aren\'t in a voice-channel.')
            return

        if self.sent_embeds:
            self.remove_embeds()

        self.stream_to_vc(
            message,
            target_channel,
            valid_track_url=is_valid_track_url,
            valid_youtube_url=is_valid_youtube_url,
            search_string=search_string,
            join=True
        )
