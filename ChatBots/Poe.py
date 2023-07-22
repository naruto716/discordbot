from Config import *
import poe
from Abstract.AbstractChatBot import *
from datetime import datetime, timedelta

"""
{
  "capybara": "Sage",
  "a2": "Claude-instant",
  "nutria": "Dragonfly",
  "a2_100k": "Claude-instant-100k",
  "beaver": "GPT-4",
  "chinchilla": "ChatGPT",
  "a2_2": "Claude+"
}
"""


class Poe(ChatBotStreamableAbstract):
    def __init__(self, engine_name):
        """
        {
          "capybara": "Sage",
          "a2": "Claude-instant",
          "nutria": "Dragonfly",
          "a2_100k": "Claude-instant-100k",
          "beaver": "GPT-4",
          "chinchilla": "ChatGPT",
          "a2_2": "Claude+"
        }
        """
        self.chatbot = poe.Client(POE_TOKEN)
        self.engine_name = engine_name
        self.previous_time = datetime.now()

    @staticmethod
    @abstractmethod
    def get_instance() -> 'Poe':
        pass

    def reset_connection(self):
        time_diff = datetime.now() - self.previous_time
        if time_diff > timedelta(minutes=10):
            self.chatbot = poe.Client(POE_TOKEN)
            self.previous_time = datetime.now()

    def get_response(self, message, context):
        self.reset_connection()
        context_message = self.get_context_message(context, self.engine_name)
        chunk = {}
        try:
            for chunk in self.chatbot.send_message(self.engine_name, context_message):
                pass
            return chunk["text"]
        except Exception as e:
            self.__class__.reset_instance()
            raise Exception(f"{str(e)}\nThe system has reset your current chat model without affecting the context in hopes of fixing the issue, you can try your request again")

    def get_context_message(self, context, engine_name, assistant_prompt="assistant:\n", max_token_count=1024):
        self.chatbot.purge_conversation(self.engine_name)
        ls = [assistant_prompt]
        context_list = context.get_context()
        token_counter = ChatBotAbstract.get_token_count(assistant_prompt, engine_name)
        for dic in context_list[::-1]:
            string_to_insert = self.format_context(dic)
            new_token_count = ChatBotAbstract.get_token_count(string_to_insert, engine_name)
            if token_counter + new_token_count > max_token_count:  # max token count
                break
            ls.insert(
                0,
                string_to_insert
            )
            token_counter += new_token_count
        return ''.join(ls)

    def get_stream_generator(self, message, context):
        self.reset_connection()
        retry_num = 0
        while retry_num <= 2: # retry 2 times
            try:
                context_message = self.get_context_message(context, self.engine_name)
                return self.chatbot.send_message(self.engine_name, context_message)
            except Exception as e:
                retry_num += 1
                self.__class__.reset_instance()
                raise Exception(f"{str(e)}\nThe system has reset your current chat model without affecting the context in hopes of fixing the issue, you can try your request again")

    def translate_stream_response(self, stream_response):
        # return stream_response
        counter = 0
        chunk = {}
        try:
            for chunk in stream_response:
                if counter == 20:
                    yield chunk["text"]
                    counter = 0
                counter += 1
            yield chunk["text"]
        except Exception as e:
            self.__class__.reset_instance()
            raise Exception(f"{str(e)}\nThe system has reset your current chat model without affecting the context in hopes of fixing the issue, you can try your request again")

    def reset(self):
        self.chatbot.purge_conversation(self.engine_name)

    @classmethod
    def reset_instance(cls):
        if hasattr(cls, '_instance'):
            cls._instance = None


class Gpt4Poe(Poe):
    _instance = None

    def __init__(self):
        if Gpt4Poe._instance is None:
            super().__init__("beaver")
        else:
            raise Exception("This class is a singleton!")

    def get_context_message(self, context, engine_name, assistant_prompt="assistant:\n", max_token_count=1024):
        return super().get_context_message(context, engine_name, assistant_prompt="assistant:\n", max_token_count=2048)

    @staticmethod
    def get_instance() -> 'Gpt4Poe':
        if Gpt4Poe._instance is None:
            Gpt4Poe._instance = Gpt4Poe()
        return Gpt4Poe._instance


class ClaudePlusPoe(Poe):
    _instance = None

    def __init__(self):
        if ClaudePlusPoe._instance is None:
            super().__init__("a2_2")
        else:
            raise Exception("This class is a singleton!")

    def get_context_message(self, context, engine_name, assistant_prompt="assistant:\n", max_token_count=1024):
        return super().get_context_message(context, engine_name, assistant_prompt="Reply to the above message based on the given context as you would with a normal context. Don't say anything else.", max_token_count=2048)

    @staticmethod
    def get_instance() -> 'ClaudePlusPoe':
        if ClaudePlusPoe._instance is None:
            ClaudePlusPoe._instance = ClaudePlusPoe()
        return ClaudePlusPoe._instance


class ClaudePoe(Poe):
    _instance = None

    def __init__(self):
        if ClaudePoe._instance is None:
            super().__init__("a2")
        else:
            raise Exception("This class is a singleton!")

    def get_context_message(self, context, engine_name, assistant_prompt="assistant:\n", max_token_count=1024):
        return super().get_context_message(context, engine_name, assistant_prompt="Reply to the above message based on the given context as you would with a normal context. Don't say anything else.", max_token_count=2048)

    @staticmethod
    def get_instance() -> 'ClaudePoe':
        if ClaudePoe._instance is None:
            ClaudePoe._instance = ClaudePoe()
        return ClaudePoe._instance


class GooglePalmPoe(Poe):
    _instance = None

    def __init__(self):
        if GooglePalmPoe._instance is None:
            super().__init__("acouchy")
        else:
            raise Exception("This class is a singleton!")

    @staticmethod
    def get_instance() -> 'GooglePalmPoe':
        if GooglePalmPoe._instance is None:
            GooglePalmPoe._instance = GooglePalmPoe()
        return GooglePalmPoe._instance

    def translate_stream_response(self, stream_response):
        # return stream_response
        chunk = {}
        for chunk in stream_response:
            pass
        yield chunk["text"]


class Gpt35Poe(Poe):
    _instance = None

    def __init__(self):
        if Gpt35Poe._instance is None:
            super().__init__("chinchilla")
        else:
            raise Exception("This class is a singleton!")

    @staticmethod
    def get_instance() -> 'Gpt35Poe':
        if Gpt35Poe._instance is None:
            Gpt35Poe._instance = Gpt35Poe()
        return Gpt35Poe._instance
