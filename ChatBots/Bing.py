from Abstract.AbstractChatBot import ChatBotStreamableAbstract
from Config import *
import json
from EdgeGPT.EdgeGPT import Chatbot


class Bing(ChatBotStreamableAbstract):
    def __init__(self, engine):
        self.chatbot = Chatbot(api_key=CHAT_GPT_API_KEY, engine=engine)

    @staticmethod
    def get_instance() -> 'ChatGPTOfficial':
        cookies = json.loads(open("./path/to/cookies.json", encoding="utf-8").read())  # might omit cookies option
        bot = await Chatbot.create(cookies=cookies)

    def set_context(self, context):
        self.chatbot.reset(convo_id=context.get_context_id(), system_prompt=context.get_system_prompt())
        context_list = context.get_context()
        for dic in context_list[:-1]:
            self.chatbot.add_to_conversation(dic["content"], dic["role"], convo_id=context.get_context_id())

    def get_response(self, message, context):
        self.set_context(context)
        return self.chatbot.ask(message, convo_id=context.get_context_id())

    def get_stream_generator(self, message, context):
        self.set_context(context)
        return self.chatbot.ask_stream(message, convo_id=context)

    def translate_stream_response(self, stream_response):
        # return stream_response
        message_list = []
        counter = 0
        for data in stream_response:
            message_list.append(data)
            if counter == 20:
                yield ''.join(message_list)
                counter = 0
            counter += 1
        yield ''.join(message_list)

    def reset(self, context, system_prompt=None):
        self.chatbot.reset(convo_id=context, system_prompt=system_prompt)