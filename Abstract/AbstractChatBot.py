from abc import ABC, abstractmethod
import tiktoken


class ChatBotAbstract:  # abstract chatbot class
    @abstractmethod
    def get_response(self, message, context):
        pass

    @staticmethod
    def tokenize(text, engine):
        engine_dict = {
            "capybara": "gpt-3.5-turbo",
            "beaver": "gpt-4",
            "chinchilla": "gpt-3.5-turbo",
        }

        if engine in engine_dict:
            engine = engine_dict[engine]
        else:
            engine = "gpt-3.5-turbo"  # Use this by default, might not be accurate though
        encoding = tiktoken.encoding_for_model(engine)
        return encoding.encode(text)

    @staticmethod
    def get_token_count(text, engine):
        return len(ChatBotAbstract.tokenize(text, engine))

    def get_context_message(self, context, engine_name, assistant_prompt="assistant:\n", max_token_count=1024):
        ls = [assistant_prompt]
        context_list = context.get_context()
        token_counter = ChatBotAbstract.get_token_count(assistant_prompt, engine_name)
        for i in range(len(context_list) - 2, -1, -1):
            dic = context_list[i]
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

    def format_context(self, context_dict) -> str:
        return str.format("{}:\n{}\n\n", context_dict["role"], context_dict["content"])


class ChatBotStreamableAbstract(ChatBotAbstract):  # abstract chatbot class
    def get_stream_response(self, message, context):  # public, yields the message to print each time
        stream_generator = self.get_stream_generator(message, context)
        return self.translate_stream_response(stream_generator)

    @abstractmethod
    def get_stream_generator(self, message, context):
        pass

    @abstractmethod
    def translate_stream_response(self, stream_response):
        pass
