from discord.ext import commands
from utils import sqlite, eventer


class Counter(sqlite.Table):
    user_id = sqlite.Column("BIGINT", nullable=False, primary_key=True)
    amount = sqlite.Column("INT", nullable=False, default=0)


class H(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event = eventer.Event(self.bot, "h", self.bot.event_config["guild_id"])

    @commands.Cog.listener()
    async def on_ready(self):
        await self.event.get_channel(
            self.bot.event_config["category_id"],
            slowmode_delay=5
        )

    async def append_h(self, user_id: int):
        data = self.bot.pool.fetchrow(
            "SELECT * FROM counter WHERE user_id=?", (user_id,)
        )

        if not data:
            return self.bot.pool.execute(
                "INSERT INTO counter VALUES (?, ?)", (user_id, 1)
            )
        return self.bot.pool.execute(
            "UPDATE counter SET amount=? WHERE user_id=?",
            (data["amount"] + 1, user_id)
        )

    async def detect_h(self, msg, edited: bool = False):
        if not self.event.channel:
            await self.event.get_channel()
            return False
        if msg.channel.id != self.event.channel.id:
            return False  # This isn't the event channel...

        if msg.author.id == self.bot.user.id:
            return False  # Don't you fucking dare loop!
        if msg.author.bot:
            return await msg.delete()  # No bots allowed...

        if msg.content != "h":
            await msg.delete()
            extra = ", editing does not help you either..." if edited else ""
            await msg.channel.send(
                f"**{msg.author}** you are only allowed to say **h**{extra}",
                delete_after=5
            )
            return False

        return True  # This message is OK

    async def cog_before_invoke(self, ctx):
        """ If bot commands are used in event channel """
        if self.event.channel:
            if ctx.channel.id == self.event.channel.id:
                raise commands.CheckFailure()

    @commands.Cog.listener()
    async def on_message(self, msg):
        if not await self.detect_h(msg):
            return
        await self.append_h(msg.author.id)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not await self.detect_h(after):
            return

    @commands.group(invoke_without_command=True)
    async def h(self, ctx):
        """ Your H counter """
        if not self.event.channel:
            return await ctx.send("The event hasn't started yet!")

        data = self.bot.pool.fetchrow(
            "SELECT * FROM counter WHERE user_id=?", (ctx.author.id,)
        )

        if not data:
            return await ctx.send(f"You have not said **h** in {self.event.channel.mention} yet...")
        await ctx.send(
            f"**{ctx.author}**, you have said h **{data['amount']:,} time(s)** "
            f"inside {self.event.channel.mention}"
        )

    @h.command(name="stats", aliases=["statistics", "leaderboard", "lb"])
    async def h_stats(self, ctx):
        """ H statistics """
        data = self.bot.pool.fetch("SELECT * FROM counter ORDER BY amount DESC LIMIT 10")
        if not data:
            return await ctx.send("No one has said h yet...")

        h_spammers = "\n".join([
            f"{g['amount']:<7,} {self.bot.get_user(g['user_id']) or 'Unknown...'}"
            for g in data
        ])

        await ctx.send(
            f"📊 __Top {len(data)} `h` spammers in **{ctx.guild.name}**__"
            f"```fix\n{h_spammers}```"
        )


def setup(bot):
    bot.add_cog(H(bot))
