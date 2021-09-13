import discord
import time

from utils import default
from discord.ext.commands import AutoShardedBot, DefaultHelpCommand, errors


class Bot(AutoShardedBot):
    def __init__(self, *args, prefix=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = prefix

    async def on_ready(self):
        print(f"[+] Loaded in cog {self.custom_extension_name}.py to bot...")
        self.load_extension(f"events.{self.custom_extension_name}")

        print(f"{self.user} is now ready to host events!")
        await self.change_presence(
            activity=discord.Game(type=0, name=self.custom_presence["message"]),
            status=getattr(discord.Status, self.custom_presence["status"]),
        )

    async def on_message(self, msg):
        if not self.is_ready() or msg.author.bot:
            return
        if not msg.channel.permissions_for(msg.author).send_messages:
            return

        await self.process_commands(msg)

    async def on_command_error(self, ctx, err):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            await ctx.send_help(helper)

        elif isinstance(err, errors.MissingPermissions):
            pass

        elif isinstance(err, errors.UserInputError):
            await ctx.send(err)

        elif isinstance(err, errors.CommandInvokeError):
            if "Cannot send messages to this user" in str(err):
                return await ctx.send("I can't DM the person in question due to either being blocked or trying to DM a bot.")

            timestamp = f"{int(time.time())}_{ctx.author.id}"
            await ctx.reply(
                f"#️⃣ **ERROR_{timestamp}**\n"
                "🛂 This incident will be reported back to the terminal."
            )

            print(f"ERROR_{timestamp}\n{default.traceback_maker(err.original)}")

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.MaxConcurrencyReached):
            await ctx.send("You've reached max capacity of command usage at once, please finish the previous one...")

        elif isinstance(err, errors.CommandOnCooldown):
            await ctx.send(f"⌛ This command is on cooldown, try again in {err.retry_after:.3f}")

        elif isinstance(err, errors.CommandNotFound):
            pass


class HelpFormat(DefaultHelpCommand):
    def get_destination(self, no_pm: bool = False):
        if no_pm:
            return self.context.channel
        else:
            return self.context.author

    async def send_error_message(self, error):
        destination = self.get_destination(no_pm=True)
        await destination.send(error)

    async def send_command_help(self, command):
        self.add_command_formatting(command)
        self.paginator.close_page()
        await self.send_pages(no_pm=True)

    async def send_pages(self, no_pm: bool = False):
        try:
            await self.context.message.add_reaction(chr(0x2709))
        except discord.Forbidden:
            pass

        try:
            destination = self.get_destination(no_pm=no_pm)
            for page in self.paginator.pages:
                await destination.send(page)
        except discord.Forbidden:
            destination = self.get_destination(no_pm=True)
            await destination.send("Couldn't send help to you due to blocked DMs...")
