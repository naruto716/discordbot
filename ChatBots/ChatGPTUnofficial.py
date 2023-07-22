from Config import *
from revChatGPT.V3 import Chatbot
from Abstract.AbstractChatBot import *


class ChatGPTOfficial(ChatBotStreamableAbstract):
    def __init__(self, engine):
        self.chatbot = Chatbot(api_key=CHAT_GPT_API_KEY, engine=engine)

    @staticmethod
    @abstractmethod
    def get_instance() -> 'ChatGPTOfficial':
        pass

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


class Gpt4Official(ChatGPTOfficial):
    _instance = None

    def __init__(self):
        if Gpt4Official._instance is None:
            super().__init__("gpt-4")
        else:
            raise Exception("This class is a singleton!")

    @staticmethod
    def get_instance() -> 'ChatGPTOfficial':
        if Gpt4Official._instance is None:
            Gpt4Official._instance = Gpt4Official()
        return Gpt4Official._instance


class Gpt35Official(ChatGPTOfficial):
    _instance = None

    def __init__(self):
        if Gpt35Official._instance is None:
            super().__init__("gpt-3.5-turbo")
        else:
            raise Exception("This class is a singleton!")

    @staticmethod
    def get_instance() -> 'ChatGPTOfficial':
        if Gpt35Official._instance is None:
            Gpt35Official._instance = Gpt35Official()
        return Gpt35Official._instance
