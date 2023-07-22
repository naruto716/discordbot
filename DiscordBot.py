import discord
from discord.ext import commands
from Abstract.AbstractChatClient import AbstractChatClient
from DiscordModel import DiscordModel, PermissionManager
from BotTypes import BOT_TYPES
from Config import *
from queue import Queue
import asyncio
from Event import *


class MyView(discord.ui.View):
    def __init__(self, model, user_id):
        super().__init__()
        self.model = model
        self.permission_manager = self.model.get_permission_manager()
        self.user_perm = self.permission_manager.get_permission(user_id)

    @discord.ui.select(
        placeholder="Choose a chat model!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label=bot_name, description=bot_info["description"])
            for bot_name, bot_info in BOT_TYPES.items()
        ]
    )
    async def select_callback(self, select, interaction):
        if not self.permission_manager.check_permission(interaction.user.id, BOT_TYPES[select.values[0]]["permission"]):
            await interaction.response.send_message("You don't have permission to do this!", ephemeral=True)
            return
        await interaction.response.send_message(f"Your chat model has been set to {select.values[0]}!", ephemeral=True)
        self.model.set_model(interaction.user.id, select.values[0])


class DiscordBot(AbstractChatClient, commands.Bot):

    def __init__(self, command_prefix, intents=None):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.add_commands()
        self.model = DiscordModel(self)
        self.permission_manager = self.model.get_permission_manager()
        self.event_handler = EventHandler()

    @staticmethod
    def get_mention_list_id(message):
        return [user.id for user in message.mentions]

    async def on_ready(self):
        loop = asyncio.get_running_loop()
        loop.create_task(self.event_handler.message_loop())
        loop.create_task(self.model.clean_redundant_threads_loop())
        loop.create_task(self.model.save_data())
        print(f'We have logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return
        # command
        if message.content.startswith("!setperm"):
            await self.set_perm(message)
            return
        # message
        if not message.guild:
            await self.process_dm_message(message)
            return
        if message.content.startswith("$"):
            await self.process_server_message(message)
            return

    async def set_perm(self, message):
        if self.permission_manager.check_permission(message.author.id, 5):
            perm_level = int(message.content.split()[-1])
            mention_list = self.get_mention_list_id(message)
            if mention_list:
                for user_id in mention_list:
                    self.permission_manager.set_permission(user_id, perm_level)
                await message.reply(
                    f"Permission for {' '.join(['<@' + str(i) + '>' for i in mention_list])} has been set to {perm_level}")
        else:
            await message.reply("You don't have permission to do this!")

    async def process_server_message(self, message):
        await message.channel.trigger_typing()
        self.model.process_message(message, message.content[1:])

    async def process_dm_message(self, message):
        await message.channel.trigger_typing()
        self.model.process_message(message, message.content)

    def add_commands(self):
        @self.slash_command(name="setmodel", description="Select the ChatBot model")
        async def setmodel(ctx):
            await ctx.respond(view=MyView(self.model, ctx.author.id), ephemeral=True)
            return

        @self.slash_command(name="stream", description="Toggle stream mode")
        async def stream(ctx):
            stream_mode = self.model.toggle_stream_mode(ctx)
            await ctx.respond(f"Stream mode is now turned {'on' if stream_mode else 'off'}", ephemeral=True)
            return

        @self.slash_command(name="global", description="Use the global context in the current channel")
        async def global_context(ctx):
            own_context = self.model.toggle_own_context(ctx)
            await ctx.respond(f"Global context is now turned {'off' if own_context else 'on'}", ephemeral=True)
            return

        @self.slash_command(name="reset", description="Reset chat history")
        async def reset(ctx):
            if self.model.reset_context(ctx):
                await ctx.respond("Chat history has been reset", ephemeral=True)
            else:
                await ctx.respond("Chat history is already empty", ephemeral=True)
            return

    def enqueue_event(self, event: Event):
        self.event_handler.add_event(event)


class EventHandler:
    def __init__(self):
        self.queue: Queue = Queue()

    async def message_loop(self):
        while True:
            while not self.queue.empty():
                event: Event = self.queue.get()
                await event.process()
                self.queue.task_done()
            await asyncio.sleep(0.1)

    def add_event(self, event: Event):
        self.queue.put(event)


def main():
    command_prefix = "$"
    intents = discord.Intents(messages=True, message_content=True, guilds=True, members=True, reactions=True)
    bot = DiscordBot(command_prefix, intents)
    bot.run(DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    main()
