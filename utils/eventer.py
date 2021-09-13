class Event:
    def __init__(self, bot, channel_name: str, guild_id: int):
        self.bot = bot
        self.channel_name = channel_name
        self.guild_id = guild_id
        self.channel = None

    async def get_channel(self, category_id: int = None, *args, **kwargs):
        """ Get the current event channel """
        guild = self.bot.get_guild(self.guild_id)
        self.channel = next(
            (c for c in guild.text_channels if c.name == self.channel_name), None
        )

        if self.channel:
            return self.channel

        await self.create_channel(category_id, *args, **kwargs)
        return self.channel

    async def create_channel(self, category_id: int = None, *args, **kwargs):
        """ Easily create a channel that the event runs in """
        if self.channel:
            return self.channel

        if category_id:
            self.channel = await self.bot.get_channel(category_id).create_text_channel(
                self.channel_name, *args, **kwargs
            )
        else:
            self.channel = await self.bot.get_guild(self.guild_id).create_text_channel(
                self.channel_name, *args, **kwargs
            )

        return self.channel

    async def edit_channel(self, *args, **kwargs):
        """ Change the event channel """
        if not self.channel:
            raise ValueError("No channel to edit...")
        return await self.channel.edit(*args, **kwargs)
