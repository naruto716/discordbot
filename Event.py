from abc import ABC, abstractmethod


class ModelEvent:
    @abstractmethod
    def process(self):
        pass


class Event(ModelEvent):
    def _init(self, discord_object, response):  # object is the object is a command or message
        self.object = discord_object
        self.response = response

    def get_object(self):
        return self.object

    def get_response(self):
        return self.response

    @abstractmethod
    async def process(self):
        pass


class DiscordStreamInitMessageEvent(Event):
    def __init__(self, discord_object, response, out_return_message_list: list):
        super()._init(discord_object, response)
        out_return_message_list.clear()
        self.out_return_message_list = out_return_message_list

    async def process(self):
        try:
            if self.response:
                message = await self.object.reply(self.response)
                self.out_return_message_list.append(message)
        except Exception as e:
            await self.object.reply("An error occurred when generating your response. You might want to reset the conversation or switch to other engines.\nError details:\n" + str(e))


class DiscordStreamMessageEditEvent(Event):
    def __init__(self, discord_object, response, initial_message_list: list):
        super()._init(discord_object, response)
        self.initial_message_list = initial_message_list

    async def process(self):
        try:
            if len(self.initial_message_list) > 0:
                await self.initial_message_list[0].edit(content=self.response)
        except Exception as e:
            await self.object.reply("An error occurred when generating your response. You might want to reset the conversation or switch to other engines.\nError details:\n" + str(e))


class DiscordMessageEvent(Event):
    def __init__(self, discord_object, response):
        super()._init(discord_object, response)

    async def process(self):
        try:
            if self.response:
                await self.object.reply(self.response)
        except Exception as e:
            await self.object.reply("An error occurred when generating your response. You might want to reset the conversation or switch to other engines.\nError details:\n" + str(e))
