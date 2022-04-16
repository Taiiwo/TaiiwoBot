from taiiwobot import Plugin
import time


class Moderator(Plugin):
    def __init__(self, bot):
        self.bot = bot
        if not self.bot.server.type == "discord":
            return
        import discord
        import asyncio

        self.discord = discord
        self.asyncio = asyncio

        self.db = self.bot.util.get_db()["admin"]

        async def delete_entry(entry):
            self.db.remove_all({"user": entry["user"], "server": entry["server"]})

        # setup coroutines for unmuting users muted in a previous session
        for mute in self.db.find({"type": "mute", "lifted": False}):
            if not mute["end"]:
                continue
            duration = (mute["end"] - time.time()) if mute["end"] >= time.time() else 0
            server = self.bot.server.client.get_guild(mute["server"])
            user = server.get_member(mute["user"])
            mute_role = self.get_mute_role(server)

            self.bot.server.gaysyncio(
                [
                    # wait until their sentence is up
                    [self.asyncio.sleep, (duration,), {}],
                    # remove the entry from the db
                    [self.lift_action, ("mute", mute["user"], mute["server"]), {}],
                    # remove their role
                    [self.remove_role, (user, mute_role), {}],
                ]
            )

        for ban in self.db.find({"type": "ban", "lifted": False}):
            if not ban["end"]:
                continue
            duration = (ban["end"] - time.time()) if ban["end"] >= time.time() else 0
            server = self.bot.server.client.get_guild(ban["server"])
            user = self.bot.server.client.get_user(ban["user"])

            self.bot.server.gaysyncio(
                [
                    # wait until their sentence is up
                    [self.asyncio.sleep, (duration,), {}],
                    # remove the entry from the db
                    [self.lift_action, ("ban", ban["user"], ban["server"]), {}],
                    # remove their role
                    [self.unban, (server, user), {}],
                ]
            )

        self.interface = bot.util.Interface(
            "mod",  # plugin name
            "A command for community moderators for performing priviledged actions",
            [],
            self.root,  # main function
            subcommands=[  # list of subcommands
                bot.util.Subcommand(
                    "mute",  # invoked with $template sub <args/flags>
                    # subcommand description
                    "Mutes a user for a specified time. Usage: $mod mute [<user>...]",
                    [
                        "f forever Mute the user forever 0",
                        "d days Number of days the user is muted for 1",
                        "h hours Number of hours the user is muted for 1",
                        "m minutes Number of minutes the user is muted for 1",
                        "r reason The reason for their mute 1",
                    ],  # subcommand flags
                    self.mute,  # subcommand function
                ),
                bot.util.Subcommand(
                    "ban",
                    "Bans a user for a specified period of time. Usage $mod ban [<user>...]",
                    [
                        "f forever Ban the user forever 0",
                        "d days Number of days the user is banned for 1",
                        "h hours Number of hours the user is banned for 1",
                        "m minutes Number of minutes the user is banned for 1",
                        "r reason The reason for their ban 1",
                    ],
                    self.ban,
                ),
                bot.util.Subcommand(
                    "add-role",
                    "adds a mod role for this server. Args: <role>",
                    [],
                    self.add_role_command,
                ),
                bot.util.Subcommand(
                    "remove-role",
                    "removes a mod role for this server. Args: <role>",
                    [],
                    self.remove_role_command,
                ),
            ],
        ).listen()  # sets the on message callbacks and parses messages

    # flags are parsed and passed to the assigned function like so:
    # *args catches all uncaught command arguments as an array.
    @Plugin.authenticated
    def root(self, message, *args):
        self.interface.help(message.target, self)

    @Plugin.authenticated
    def add_role_command(self, message, role_name):
        matching_role = False
        for role in message.raw_message.guild.roles:
            if "<@&%s>" % role.id == role_name:
                matching_role = role
                del role
                break
        if not matching_role:
            self.bot.msg(message.target, "Invalid role")
            return False
        if not message.server in self.bot.config["plugin_config"]:
            self.bot.config["plugin_config"][str(message.server)] = {"mod_roles": []}
        self.bot.config["plugin_config"][str(message.server)]["mod_roles"].append(
            matching_role.id
        )
        self.bot.config.save_config()
        self.bot.msg(message.target, "Moderator role added.")

    @Plugin.authenticated
    def remove_role_command(self, message, role_name):
        matching_role = False
        for role in message.raw_message.guild.roles:
            if "<@&%s>" % role.id == role_name:
                matching_role = role
                del role
                break
        if not matching_role.id:
            self.bot.msg(message.target, "Invalid role")
        elif not str(message.server) in self.bot.config["plugin_config"]:
            # TODO: this should be a RuntimeError
            self.bot.msg(message.target, "Mod role does not exist")
        elif (
            not matching_role.id
            in self.bot.config["plugin_config"][str(message.server)]["mod_roles"]
        ):
            self.bot.msg(message.target, "This role does not have admin privs")
        else:
            self.bot.config["plugin_config"][str(message.server)]["mod_roles"].remove(
                matching_role.id
            )
            print(self.bot.config)
            self.bot.config.save_config()
            self.bot.msg(message.target, "Moderator role removed.")

    @Plugin.authenticated
    def ban(
        self,
        message,
        *args,
        days="0",
        hours="0",
        minutes="0",
        reason=None,
        forever=False
    ):
        print("sanity")
        if days.isnumeric() and hours.isnumeric() and minutes.isnumeric():
            duration = (
                (int(days) * 24 * 60 * 60)
                + (int(hours) * 60 * 60)
                + (int(minutes) * 60)
            )
            duration = 60 * 60 if duration == 0 else duration
        else:
            raise self.bot.util.RuntimeError(
                "Invalid duration. Must be numeric!", message.target, self
            )

        users = message.raw_message.mentions

        def ban(r):
            for user in users:
                calls = [
                    [
                        user.guild.ban,
                        (user,),
                        {"reason": reason, "delete_message_days": 0},
                    ]
                ]
                if not forever:
                    calls += [
                        [self.asyncio.sleep, (duration,), {},],
                        [self.unban, (user.guild, user), {}],
                    ]
                self.bot.server.gaysyncio(calls)
                # send audit message
                self.bot.msg(
                    self.bot.config["audit_channel"],
                    "<@%s> was banned by <@%s> in <#%s> for %s mins (reason: %s)"
                    % (
                        user.id,
                        message.author,
                        message.target,
                        "infinite" if forever else duration / 60,
                        reason,
                    ),
                )
                # save to database
                self.db.insert_one(
                    {
                        "type": "ban",
                        "user": user.id,
                        "server": user.guild.id,
                        "end": None if forever else time.time() + duration,
                        "reason": reason,
                        "lifted": False,
                    }
                )
                # Send mod confirmation
                self.bot.msg(message.target, "User was banned.", follows=message)

        self.bot.server.menu(
            message.target,
            message.author,
            "Are you sure you wish you ban %s users for %s minutes?"
            % (
                len(message.raw_message.mentions),
                "infinite" if forever else duration / 60,
            ),
            ync=[ban, lambda r: False, lambda r: False],
            delete_after=120,
        )

    def get_mute_role(self, guild):
        mute_role = False
        for role in guild.roles:
            if role.name == "muted":
                mute_role = role
                break
        return mute_role

    # marks an action as lifted in the db
    async def lift_action(self, action, user, server):
        self.db.update_one(
            {"type": action, "user": user, "server": server, "lifted": False},
            {"$set": {"lifted": True}},
        )

    @Plugin.authenticated
    def mute(
        self,
        message,
        *args,
        days="0",
        hours="0",
        minutes="0",
        reason=None,
        forever=False
    ):
        if days.isnumeric() and hours.isnumeric() and minutes.isnumeric():
            duration = (
                (int(days) * 24 * 60 * 60)
                + (int(hours) * 60 * 60)
                + (int(minutes) * 60)
            )
            duration = 60 * 60 if duration == 0 else duration
        else:
            raise self.bot.util.RuntimeError(
                "Invalid duration. Must be numeric!", message.target, self
            )
        # get the mute role if exists
        mute_role = self.get_mute_role(message.raw_message.guild)
        if not mute_role:
            raise self.bot.util.RuntimeError(
                "`muted` role not created.", message.target, self
            )
        users = message.raw_message.mentions

        def mute(r):
            for user in users:
                calls = []
                # give the mute role to the user
                calls.append([self.add_role, (user, mute_role), {}])
                if not forever:
                    # wait until their sentence is up
                    calls.append([self.asyncio.sleep, (duration,), {}])
                    # lift from the db
                    calls.append(
                        [self.lift_action, ("mute", user.id, user.guild.id), {}]
                    )
                    # remove their role
                    calls.append([self.remove_role, (user, mute_role), {}])
                self.bot.server.gaysyncio(calls)

                if self.db.find_one(
                    {"user": user.id, "server": user.guild.id, "lifted": False}
                ):
                    raise self.bot.util.RuntimeError(
                        "User is already muted. Ping @Taiiwo if you would like their mute extending, as it is through his laziness that this error isn't replaced with some code that automatically extends the mute.",
                        message.target,
                        self,
                    )

                # store the mute so we can continue the sentence after restart
                self.db.insert_one(
                    {
                        "type": "mute",
                        "user": user.id,
                        "server": user.guild.id,
                        "end": None if forever else time.time() + duration,
                        "reason": reason,
                        "mod": message.author,
                        "lifted": False,
                    }
                )

                # send a message to the audit log
                self.bot.msg(
                    self.bot.config["audit_channel"],
                    "<@%s> was muted for %s minutes by <@%s> in channel <#%s> (reason: %s)"
                    % (
                        user.id,
                        "infinite" if forever else duration / 60,
                        message.author,
                        message.target,
                        reason,
                    ),
                )

                # Send mod confirmation
                self.bot.msg(message.target, "User was muted.", follows=message)

        self.bot.server.menu(
            message.target,
            message.author,
            "Are you sure you wish you mute %s users for %s minutes?"
            % (
                len(message.raw_message.mentions),
                "infinite" if forever else duration / 60,
            ),
            ync=[mute, lambda r: False, lambda r: False],
            delete_after=120,
        )

    async def add_role(self, user, role):
        # give the user the mute role
        await user.add_roles(role)

    async def remove_role(self, user, role):
        # remove the mute role from the user
        await user.remove_roles(role)
        self.bot.msg(self.bot.config["audit_channel"], "<@%s> was unmuted" % user.id)

    async def unban(self, server, user):
        await server.unban(user)
        self.bot.msg(self.bot.config["audit_channel"], "<@%s> was unbanned" % user.id)
