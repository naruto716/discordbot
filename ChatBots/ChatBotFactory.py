from ChatBots.ChatGPTUnofficial import *
from ChatBots.Poe import *
from BotTypes import *


class ChatBotFactory:
    def __init__(self):
        raise RuntimeError("ChatBotFactory should not be instantiated. Use the static method get_bot instead.")

    @staticmethod
    def get_bot(bot_type="default"):
        if bot_type in BOT_TYPES:
            return BOT_TYPES[bot_type]["class"].get_instance()
        elif bot_type == "default":  # default bot
            return DEFAULT_ENGINE.get_instance()
        else:
            raise ValueError("Invalid bot type: " + bot_type)
