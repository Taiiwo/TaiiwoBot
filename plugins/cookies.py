from taiiwobot import Plugin
import math
import time
import random
import base64
import asyncio


class Cookies(Plugin):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.util.get_db()["cookies"]
        stock = [
            # emoji, description, price
            ["🥛", "Milk", 5, "FFFFFF"],
            ["🥞", "Blueberry Pancakes", 20, "5859E0"],
            ["🥓", "Bacon", 15, "CF5F18"],
            ["🥩", "Steak", 30, "683618"],
            ["🥗", "Salad", 10, "83ce89"],
            ["🍜", "Ramen", 15, "fee379"],
            ["🍚", "Rice", 12, "fffdd9"],
            ["🧁", "Cupcake", 15, "F0A0AE"],
            ["🍩", "Doughnut", 15, "966c4c"],
            ["🍵", "Green Tea", 3, "BAD80A"],
            ["☕", "Coffee", 5, "99643C"],
            ["🍶", "Sake", 10, "eae6d2"],
        ]
        self.stock = stock
        self.cross_png = base64.decodestring(
            b"iVBORw0KGgoAAAANSUhEUgAAAA8AAAAPBAMAAADJ+Ih5AAAAG1BMVEVHcEzdLkTdLkTdLkTdLkTdLkTdLkTdLkTdLkSk3kMyAAAACHRSTlMAHdvcF1I6OV1IEpIAAABdSURBVAjXNc0xDoAwCAXQz6Bz056gi/YIjI2me0fP08Ue2w8qC+EFPlgqWA24MruUjnMEII4K0UwwTiNEU9LuQJoOwDpv74ifSNnUd3iSjCzDsnDYlJj8/tKO//sD7u0O9OvZ4HcAAAAASUVORK5CYII="
        )
        self.cookie_png = base64.decodestring(
            b"iVBORw0KGgoAAAANSUhEUgAAAA8AAAAPCAMAAAAMCGV4AAAAVFBMVEXboITboITboITboITboITboITboIRHcEzboITboITboITboITboITboITboITboITboITZnoLEiW/XnICkaFLRlnu1emK+g2rLkHaWWEKNTDeTUz4PnvnzAAAAEXRSTlP/KbtPZ1lAAHIzBxbM18Wl5ZgtcSsAAACHSURBVAjXLY8JDoUwCESndte/QV2q3v+eH6gklHmBMBRZo5YQ0qwKkvEFCXq7wVEJfDYU5Yq1aZsJ8MITCNvebOg3o2o9LrYVSCgm9k3L2oIwW4/vQ96CSNeqvJ9svBCPXRYV+fvIJrYf8XOmO+jYUPU+ceh315Ew7vd6EjCl5z85u1D8YuoP8/AGR+6gjvEAAAAASUVORK5CYII="
        )
        self.interface = bot.util.Interface(
            "cookie",  # plugin name
            "CookiEconomy plugin",  # plugin description
            [],
            self.some_func,  # main function
            subcommands=[  # list of subcommands
                bot.util.Subcommand(
                    "balance",  # invoked with $template sub <args/flags>
                    # subcommand description
                    "Check your cookie balance. Args: [uid]",
                    [],
                    self.balance,  # subcommand function
                ),
                bot.util.Subcommand(
                    "summon",  # invoked with $template sub <args/flags>
                    # subcommand description
                    "Summons a cookie, for testing and displays of admin dominance",
                    [],
                    self.summon,  # subcommand function
                ),
                bot.util.Subcommand(
                    "drop",  # invoked with $template sub <args/flags>
                    "Drops one of your cookies into the channel",  # subcommand description
                    [],
                    self.drop,  # subcommand function
                ),
                bot.util.Subcommand(
                    "shop",  # invoked with $template sub <args/flags>
                    "Opens the cookie shop",  # subcommand description
                    [],
                    self.shop,  # subcommand function
                ),
                bot.util.Subcommand(
                    "give",  # invoked with $template sub <args/flags>
                    "Pay someone in cookie. Args: <@recipient> <amount>",  # subcommand description
                    [],
                    self.give,  # subcommand function
                ),
                bot.util.Subcommand(
                    "test",  # invoked with $template sub <args/flags>
                    "Test the new cookie drop method",  # subcommand description
                    [],
                    self.test,  # subcommand function
                ),
                bot.util.Subcommand(
                    "lunchbox",  # invoked with $template sub <args/flags>
                    "Check the contents of your lunchbox",  # subcommand description
                    [],
                    self.lunchbox,  # subcommand function
                ),
                bot.util.Subcommand(
                    "offer",
                    "Offer to trade a number of cookies for something out of someone's lunchbox. Args: <target>",
                    [
                        "i item The name of the item you wish to trade for 1",
                        "a amount The amount of cookies you are willing to trade 1",
                        "c confirm Skip the confirmation before the trade offer 0",
                    ],
                    self.offer,
                ),
                bot.util.Subcommand(
                    "dice",
                    "Gamble your cookies in a dice game! Args: <amount>",
                    [
                        "p payout Desired payout multiplier 1",
                        "u under The goal to roll under 1",
                        "o over The goal to roll over 1",
                    ],
                    self.dice,
                ),
            ],
        ).listen()  # sets the on message callbacks and parses messages

        @bot.on("message", self.name)
        def spawn_cookie(message):
            if message.content and (
                message.content[0] == "$"
                or message.author == self.bot.server.me()
                or message.raw_message.author.bot
            ):
                return False
            roll = random.randint(0, 819200)
            if roll < 1:
                self.bot.msg(
                    message.target,
                    "A Steak appeared",
                    reactions=(("🥩", self.collect_item),),
                    delete_after=60,
                )
            elif roll < 2:
                self.bot.msg(
                    message.target,
                    "Some Blueberry Pancakes appeared",
                    reactions=(("🥞", self.collect_item),),
                    delete_after=60,
                )
            elif roll < 4:
                self.bot.msg(
                    message.target,
                    "A Doughnut appeared",
                    reactions=(("🍩", self.collect_item),),
                    delete_after=60,
                )
            elif roll < 8:
                self.bot.msg(
                    message.target,
                    "A Cupcake appeared",
                    reactions=(("🧁", self.collect_item),),
                    delete_after=60,
                )
            elif roll < 16:
                self.bot.msg(
                    message.target,
                    "Some Ramen appeared",
                    reactions=(("🍜", self.collect_item),),
                    delete_after=60,
                )
            elif roll < 32:
                self.bot.msg(
                    message.target,
                    "Some Bacon appeared",
                    reactions=(("🥓", self.collect_item),),
                    delete_after=60,
                )
            elif roll < 64:
                self.bot.msg(
                    message.target,
                    "Some Rice appeared",
                    reactions=(("🍚", self.collect_item),),
                    delete_after=60,
                )
            elif roll < 128:
                self.bot.msg(
                    message.target,
                    "Some Sake appeared",
                    reactions=(("🍶", self.collect_item),),
                    delete_after=60,
                )
            elif roll < 256:
                self.bot.msg(
                    message.target,
                    "A Salad appeared",
                    reactions=(("🥗", self.collect_item),),
                    delete_after=60,
                )
            elif roll < 512:
                self.bot.msg(
                    message.target,
                    "A Coffee appeared",
                    reactions=(("☕", self.collect_item),),
                    delete_after=60,
                )
            elif roll < 1024:
                self.bot.msg(
                    message.target,
                    "Some Milk appeared",
                    reactions=(("🥛", self.collect_item),),
                    delete_after=60,
                )
            elif roll < 2048:
                self.bot.msg(
                    message.target,
                    "Some Green Tea appeared",
                    reactions=(("🍵", self.collect_item),),
                    delete_after=60,
                )
            elif roll < 4098:
                # cookie
                self.bot.msg(
                    message.target,
                    "A cookie appeared",
                    reactions=(("🍪", self.collect_cookie),),
                    delete_after=60,
                )

        class User:
            def __init__(self, user_id, db=self.db, init=False):
                """Object that represents a cookie-having user

                Args:
                    user_id (int): user_id of user
                    db (MongoClient, optional): The mongodb instance to reference. Defaults to self.db.
                    init (bool, optional): Should we init the user if not exists?. Defaults to False.

                Returns:
                    [type]: [description]
                """
                self.id = user_id
                self.db = db
                self.db_user = self.db.find_one({"user": self.id})
                if not self.db_user:
                    if init:
                        self.init()
                    else:
                        return None

            def init(self, cookies=0):
                cookies = cookies or 0
                if not self.db_user:
                    self.db_user = {"user": self.id, "cookies": cookies}
                    self.db.insert_one(self.db_user)

            def cookies(self):
                """Returns the number of cookies this user has

                Returns:
                    int: Number of cookies
                """
                if self.db_user:
                    return self.db_user["cookies"]
                else:
                    return 0

            def inc_cookies(self, inc: int):
                """Increment the user's cookies by a set amount

                Args:
                    inc (int): The number of cookies to increment. Can be positive

                Raises:
                    Exception: Function cannot be used to lower a user below 0 cookies
                """
                # init user with inc cookies if not exists
                if not self.db_user:
                    if inc:
                        self.init(cookies=inc)
                        return
                    else:
                        raise Exception(
                            "New user can't have negative cookies!")

                # increment the cookies
                if self.db_user["cookies"] + inc >= 0:
                    self.db_user["cookies"] += inc
                    self.update()
                else:
                    raise Exception(
                        "Existing user cannot have negative cookies!")

            def add_item(self, item: str, quantity=1):
                """Gives the user an item

                Args:
                    item (str): The emoji of the desired item
                    quantity (int, optional): The amount of item to give. Defaults to 1.
                """
                if "items" not in self.db_user:
                    self.db_user["items"] = {}
                if item[1] in self.db_user["items"]:
                    self.db_user["items"][item[1]] += quantity
                else:
                    self.db_user["items"][item[1]] = quantity
                self.update()

            def get_items(self):
                """Returns the items the user owns

                Returns:
                    Dict: List of items the user owns
                """
                return self.db_user["items"]

            def update(self):
                """Apply updates to self.db_user to the database
                """
                self.db.update({"user": self.id}, {"$set": self.db_user})

            def consume(self, emoji, context):
                """Consumes the target emoji, handing inventory and applying effects

                Args:
                    emoji (str): The emoji to apply
                    context (Message): Some message object to use as context
                """
                if (
                    bot.server.type == "discord"
                    and context.guild.me.guild_permissions.manage_roles
                ):
                    import discord

                    async def main():
                        item_a = [i for i in stock if i[0] == emoji][0]
                        roles = [
                            r for r in context.guild.roles if r.name == item_a[1]]
                        if roles:
                            role = roles[0]
                        else:
                            role = await context.guild.create_role(
                                name=item_a[1],
                                colour=discord.Colour(int(item_a[3], 16)),
                            )

                        if not "roles" in self.db_user:
                            self.db_user["roles"] = []
                        # update the user object
                        self.db_user["roles"].append(
                            {
                                "role_id": role.id,
                                "end": time.time() + item_a[2] * 60 * 60 * 24,
                                "server": context.guild.id,
                            }
                        )
                        if self.db_user["items"][item_a[1]] > 1:
                            self.db_user["items"][item_a[1]] -= 1
                        else:
                            del self.db_user["items"][item_a[1]]

                        print(self.db_user)
                        self.update()
                        # give the user the role
                        print(role)
                        await context.author.add_roles(role)
                        # wait until the role expires
                        await asyncio.sleep(item_a[2] * 60 * 60 * 24)
                        # remove the role
                        await context.author.remove_roles(role)

                    bot.server.gaysyncio(
                        [
                            [main, tuple(), {}],
                        ]
                    )

        self.User = User

        async def remove_role(uid, role):
            server = self.bot.server.client.get_guild(role["server"])
            role_obj = server.get_role(role["role_id"])
            if not role_obj:
                print("broken user: " + str(uid) + str(role))
            member = server.get_member(uid)
            if member:
                print("removing role for " + member.name)
                await member.remove_roles(role_obj)

            self.db.update(
                {"user": uid},
                {"$pull": {"roles": role}},
            )

        # set up the coroutines to remove expired roles
        for user in self.db.find({"roles": {"$exists": True}}):
            if self.bot.server.type == "discord":
                for role in user["roles"]:
                    self.bot.server.gaysyncio(
                        [
                            [asyncio.sleep, (role["end"] - time.time(),), {}],
                            [remove_role, (user["user"], role), {}],
                        ]
                    )

    # flags are parsed and passed to the assigned function like so:
    # *args catches all uncaught command arguments as an array.
    def some_func(self, message, *args):
        self.bot.msg(
            message.target,
            "You probably meant to use one of the commands. Try $cookie help",
            follows=message,
        )

    def balance(self, message, user_id=False):
        # sends a message to the channel it came from
        user = self.User(int(user_id.strip("<@!>"))
                         if user_id else message.author)
        if not user:
            self.bot.msg(message.target,
                         "You have no cookies :(", follows=message)
        else:
            self.bot.msg(
                message.target,
                "%s %s cookie%s!"
                % (
                    "That user has" if user_id else "You have",
                    user.cookies(),
                    "s" if user.cookies() > 1 else "",
                ),
                follows=message,
            )

    def summon(self, message):
        if message.author == 200329561437765652:
            self.bot.msg(
                message.target,
                "A cookie appeared",
                reactions=(("🍪", self.collect_cookie),),
                delete_after=60,
                follows=message,
            )
        else:
            self.bot.msg(message.target, "You can't do that!")

    def test(self, message):
        """An example of a method of dropping cookies that makes it harder to automate collection

        Args:
            message (Message): message object
        """
        user = self.User(message.author)
        if message.author != 200329561437765652:
            self.bot.msg(
                message.target, "1 cookie removed for being nosey", follows=message
            )
            user.inc_cookies(-1)
            return
        # if we're on discord and we have emoji perms
        if (
            self.bot.server.type == "discord"
            and message.raw_message.guild.me.guild_permissions.manage_emojis
        ):
            def remove_cookie(r): return self.User(
                r["reactor"]).inc_cookies(-1)
            r = [1, 2]
            random.shuffle(r)

            async def send_message(r1, r2):
                print(r1, r2)
                self.bot.msg(
                    message.target,
                    "A cookie appeared",
                    reactions=(
                        (r1, remove_cookie) if r[0] -
                        1 else (r2, self.collect_cookie),
                        (r1, remove_cookie) if r[1] -
                        1 else (r2, self.collect_cookie),
                    ),
                    delete_after=60,
                )
                await asyncio.sleep(1)
                await r1.delete()
                await r2.delete()

            # add emojis
            self.bot.server.gaysyncio(
                [
                    [
                        message.raw_message.guild.create_custom_emoji,
                        tuple(),
                        {"name": "cookie" +
                            str(r[0]), "image": self.cross_png},
                    ],
                    [asyncio.sleep, (0.5,), {}],
                    [
                        message.raw_message.guild.create_custom_emoji,
                        tuple(),
                        {"name": "cookie" +
                            str(r[1]), "image": self.cookie_png},
                    ],
                    [asyncio.sleep, (0.5,), {}],
                    [send_message, ("$0", "$2"), {}],
                ]
            )
        else:
            # not in discord or no perms
            self.bot.msg(
                message.target,
                "A cookie appeared",
                reactions=(("🍪", self.collect_cookie),),
                delete_after=60,
            )

    def drop(self, message):
        try:
            self.User(message.author).inc_cookies(-1)
        except:
            self.bot.msg(
                message.target, "You have no cookies to drop!", follows=message
            )
            return
        # dispense cookie
        self.bot.msg(
            message.target,
            "<@%s> dropped a cookie" % message.author,
            reactions=(("🍪", self.collect_cookie),),
            delete_after=60,
            follows=message,
        )

    def shop(self, message):
        self.bot.msg(
            message.target,
            "Welcome to the cookie shop\n%s"
            % "\n".join(
                ["[%s] %s - %s Cookies" % (e[0], e[1], e[2])
                 for e in self.stock]
            ),
            user=message.author,
            reactions=[[e[0], self.buy] for e in self.stock],
            delete_after=120,
            follows=message,
        )

    def buy(self, r):
        product = [a for a in self.stock if a[0] == r["emoji"]][0]
        user = self.User(r["reactor"])
        try:
            user.inc_cookies(-product[2])
        except:
            self.bot.msg(r["channel"], "You can't afford that!")
            return False
        user.add_item(product)
        self.bot.msg(
            r["channel"],
            "%s successfully purchased %s %s"
            % (self.bot.server.mention(r["reactor"]), product[0], product[1]),
        )

    def lunchbox(self, message):
        user = self.User(message.author)

        def consume_handler(r):
            user.consume(r["emoji"], message.raw_message)
            self.bot.msg(
                message.target,
                "%s consumes %s"
                % (self.bot.server.mention(message.author), r["emoji"]),
                follows=message,
            )

        items = [i for i in self.stock if i[1] in user.get_items()]

        if not user.db_user["items"]:
            self.bot.msg(message.target, "Your lunchbox is empty!")
        else:
            print(items)
            self.bot.msg(
                message.target,
                "You open your lunchbox:\n```%s```\nWould you like to eat/drink something?"
                % "\n".join(
                    [
                        "[%s] %s - %s" % (i[0], i[1], user.get_items()[i[1]])
                        for i in items
                    ]
                ),
                reactions=[[i[0], consume_handler] for i in items],
                user=message.author,
                follows=message,
            )

    def give(self, message, *args):
        amount = False
        for arg in args:
            if arg.isnumeric():
                amount = int(arg)
                break
        if not amount:
            return self.bot.msg(message.target, "No amount specified.", follows=message)
        targets = self.bot.server.get_mentions(message)
        if not targets:
            return self.bot.msg(
                message.target, "No recipient specified.", follows=message
            )
        else:
            target = targets[0]

        def yes(r):
            try:
                self.User(message.author).inc_cookies(-amount)
            except:
                self.bot.msg(
                    message.target,
                    "You don't have enough cookies to do that!",
                    follows=message,
                )
                return
            self.User(target).inc_cookies(amount)
            self.bot.msg(
                message.target,
                "%s gave %s %s cookies"
                % (
                    self.bot.server.mention(message.author),
                    self.bot.server.mention(target),
                    amount,
                ),
                follows=message,
            )

        self.bot.menu(
            message.target,
            message.author,
            "Are you sure you want to give %s %s cookies?"
            % (self.bot.server.mention(target), amount),
            ync=[yes, lambda r: False, lambda r: False],
            delete_after=60,
        )

    def dice(self, message, *args, payout=False, under=False, over=False):
        amount = args[0]
        roll = random.randint(1, 100)
        if payout:
            if payout.isnumeric() and int(payout) > 0:
                under = 99 / (int(payout) / 100)
                payout = int(payout) / 100
            else:
                raise self.bot.util.RuntimeError(
                    "Invalid payout quantity", message.target, self
                )
        elif over:
            if over.isnumeric() and int(over) <= 99 and int(over) > 0:
                under = 100 - int(over)
                payout = 99 / (100 - int(over))
            else:
                raise self.bot.util.RuntimeError(
                    "Invalid over quantity", message.target, self
                )
        elif under:
            if under.isnumeric() and int(under) <= 99 and int(under) > 0:
                under = int(under)
                payout = 99 / int(under)
            else:
                raise self.bot.util.RuntimeError(
                    "Invalid under quantity", message.target, self
                )
        if not under or not payout:
            # default
            under = 49
            payout = 2
        self.bot.msg(
            message.target,
            "You're betting %s cookies on getting %s or %s. If you win, you will win %s cookies. You rolled: %s"
            % (
                amount,
                100 - int(under) if over else under,
                "over" if over else "under",
                math.floor(int(amount) * payout),
                100 - roll if over else roll,
            ),
        )
        user = self.User(message.author)
        if user.cookies() < int(amount):
            self.bot.msg(message.target,
                         "You don't have enough cookies to make that bet!")
            return
        user.inc_cookies(-int(amount))
        bot = self.User(self.bot.server.me())
        bot.inc_cookies(int(amount))
        if roll <= under:
            self.bot.msg(
                message.target,
                "You win %s cookies!" % (math.floor(int(amount) * payout)),
            )
            user = self.User(message.author)
            user.inc_cookies(math.floor(int(amount) * payout))
            bot = self.User(self.bot.server.me())
            if bot.cookies() - math.floor(int(amount) * payout) <= 0:
                bot.db_user["cookies"] = 0
                bot.update()
            else:
                bot.inc_cookies(-math.floor(int(amount) * payout))
        else:
            self.bot.msg(message.target, "You lose!")

    def offer(self, message, *args, item=False, amount=False, confirm=False):
        targets = self.bot.server.get_mentions(message)
        if not targets:
            return self.bot.msg(
                message.target, "No recipient specified.", follows=message
            )
        else:
            target = self.User(targets[0])
        if amount:
            if isinstance(amount, int) or amount.isnumeric():
                amount = int(amount)
            else:
                return self.bot.msg(
                    message.target, "Amount specified is not a number!", follows=message
                )
        if item:
            for s in self.stock:
                if s[1] == item:
                    item = s
                    break
            else:
                return self.bot.msg(
                    message.target, "Unknown item specified.", follows=message
                )
        if item and amount and confirm:

            def trade(r):
                target = self.User(targets[0])
                if (
                    item[1] not in target.get_items()
                    or target.get_items()[item[1]] <= 0
                ):
                    self.bot.msg(message.target, "Nice try loser")
                    return
                try:
                    self.User(message.author).inc_cookies(-amount)
                except:
                    self.bot.msg(
                        message.target,
                        "You don't have enough cookies to do that!",
                        follows=message,
                    )
                    return
                target = self.User(targets[0])
                target.inc_cookies(amount)
                target.add_item(item, quantity=-1)
                self.User(message.author).add_item(item)
                self.bot.msg(
                    message.target,
                    "%s traded %s cookies with %s for %s"
                    % (
                        self.bot.server.mention(message.author),
                        amount,
                        self.bot.server.mention(target.id),
                        item[1],
                    ),
                    follows=message,
                )

            self.bot.menu(
                message.target,
                target.id,
                "%s has offered %s %s cookies in exchange for %s %s. Do you accept?"
                % (
                    self.bot.server.mention(message.author),
                    self.bot.server.mention(target.id),
                    amount,
                    item[0],
                    item[1],
                ),
                ync=[trade, lambda n: False, lambda c: False],
            )
        elif amount:
            self.bot.menu(
                message.target,
                message.author,
                "Are you sure you wish to offer %s cookies to %s in exchange for %s"
                % (amount, self.bot.server.mention(target.id), item[1]),
                ync=[
                    lambda y: self.offer(
                        message, item=item[1], amount=amount, confirm=True
                    ),
                    lambda n: False,
                    lambda c: False,
                ],
            )
        elif item:
            self.bot.prompt(
                message.target,
                message.author,
                "How many cookies would you like to offer?",
                lambda m: self.offer(
                    message, item=item[1], amount=m.content, confirm=confirm
                ),
            )
        else:
            answers = []

            def a(i):
                return lambda r: self.offer(
                    message, item=i, amount=amount, confirm=confirm
                )

            for item in target.get_items():
                if target.get_items()[item] >= 1:
                    for s in self.stock:
                        if s[1] == item:
                            answers.append([s[0], s[1], a(item)])
            self.bot.menu(
                message.target,
                message.author,
                "Which item would you like to make an offer for?",
                answers=answers,
            )

    def collect_cookie(self, r):
        if r["reactor"] == self.bot.server.me():
            return
        user = self.User(r["reactor"])
        self.bot.msg(
            r["channel"],
            "Cookie collected by %s" % self.bot.server.mention(r["reactor"]),
        )
        del self.bot.server.reaction_callbacks[r["message"]]
        user.inc_cookies(1)

    def collect_item(self, r):
        if r["reactor"] == self.bot.server.me():
            return
        del self.bot.server.reaction_callbacks[r["message"]]
        user = self.User(r["reactor"])

        for item in self.stock:
            if not r["emoji"] == item[0]:
                continue
            self.bot.msg(
                r["channel"],
                "%s collected by %s" % (
                    item[1], self.bot.server.mention(r["reactor"])),
            )
            return user.add_item(item)
