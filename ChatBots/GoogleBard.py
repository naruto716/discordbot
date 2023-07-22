from bardapi import Bard
from Abstract.AbstractChatBot import ChatBotAbstract
from Config import *
import requests


class GoogleBard(ChatBotAbstract):
    _instance = None
    #_chatbot = None

    def __init__(self):
        if GoogleBard._instance is None:
            pass
        else:
            raise Exception("This class is a singleton!")

    @staticmethod
    def get_instance() -> 'GoogleBard':
        if GoogleBard._instance is None:
            GoogleBard._instance = GoogleBard()
            #GoogleBard._chatbot = Bard(token=GOOGLE_BARD_TOKEN)
        return GoogleBard._instance

    def get_response(self, message, context):
        try:
            context_message = self.get_context_message(context, "google_bard")
            question = context_message + "\n" + message
            response = Bard(token=GOOGLE_BARD_TOKEN).get_answer(question)
            reply = response["content"]
            if len(response["images"]) > 0:
                reply += "\n\n[Images]\n" + '\n'.join(response["images"])
            return reply
        except Exception as e:
            self.__class__.reset_instance()
            raise Exception(
                f"{str(e)}\nThe system has reset your current chat model without affecting the context in hopes of fixing the issue, you can try your request again" + str(
                    e))

    @classmethod
    def reset_instance(cls):
        if hasattr(cls, '_instance'):
            cls._instance = None
            cls._chatbot = None

    def get_context_message(self, context, engine_name, assistant_prompt="assistant:\n", max_token_count=1024):
        return "CONTEXT_START\n" + super().get_context_message(context, engine_name, assistant_prompt="\n",
                                                               max_token_count=2048) + "\nCONTEXT_END"

    def format_context(self, context_dict) -> str:
        if context_dict["role"] == "user":
            return f"Me: {context_dict['content']}\n"
        else:
            return f"Bard: {context_dict['content']}\n"
