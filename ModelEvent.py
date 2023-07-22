from abc import ABC, abstractmethod
from Event import *
import pickle

MESSAGE_LENGTH_LIMIT = 1900


class AIEvent(ModelEvent):
    def __init__(self, response_object, message_content, context, engine, chatbot):
        # response_object = msg or cmd
        self.object = response_object
        self.message_content = message_content
        self.engine = engine
        self.context = context
        self.chatbot = chatbot

    def get_object(self):
        return self.object

    def get_message_content(self):
        return self.message_content

    @abstractmethod
    def process(self):
        pass


class DiscordMessageAIEvent(AIEvent):
    def process(self):
        try:
            message_pair = self.context.add_message_pair(self.message_content, self.object.author.id)  # context for user
            response = self.engine.get_response(self.message_content, self.context)
            message_pair.set_reply(response)  # context for response

            response_list = MessageSplitter.split_response(response)
            for message in response_list:
                self.chatbot.enqueue_event(DiscordMessageEvent(self.object, message))
        except Exception as e:
            self.chatbot.enqueue_event(DiscordMessageEvent(self.object, "An error occurred when generating your response. You might want to reset the conversation or switch to other engines.\nError details:\n" + str(e)))


class DiscordMessageStreamAIEvent(AIEvent):
    def process(self):
        try:
            message_pair = self.context.add_message_pair(self.message_content, self.object.author.id)  # context for user
            counter = 0
            response_generator = self.engine.get_stream_response(self.message_content, self.context)
            message_to_stream_list = []
            for response in response_generator:
                message_pair.set_reply(response)

                response_list = MessageSplitter.split_response(response)
                while len(message_to_stream_list) < len(response_list):
                    message_to_stream_list.append(DiscordMessageStreamAIEvent.MessageToStream(self))
                for i in range(len(response_list)):
                    message_to_stream_list[i].stream(response_list[i])
        except Exception as e:
            self.chatbot.enqueue_event(DiscordMessageEvent(self.object, "An error occurred when generating your response. You might want to reset the conversation or switch to other engines.\nError details:\n" + str(e)))

    class MessageToStream:
        def __init__(self, outer_instance):
            self.last_message = ""
            self.outer_instance = outer_instance
            self.init = False
            self.return_message_list = []

        def stream(self, message):
            if message != self.last_message:
                self.last_message = message
                if self.init is False:
                    self.init = True
                    self.outer_instance.chatbot.enqueue_event(
                        DiscordStreamInitMessageEvent(
                            self.outer_instance.object, message, self.return_message_list
                        )
                    )
                else:
                    self.outer_instance.chatbot.enqueue_event(
                        DiscordStreamMessageEditEvent(
                            self.outer_instance.object, message, self.return_message_list
                        )
                    )


class ThreadTerminationException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ThreadTerminateEvent(ModelEvent):
    def process(self):
        raise ThreadTerminationException("Thread terminated")


class DataSaveEvent(ModelEvent):
    def __init__(self, object_to_save):
        self.object = object_to_save

    def process(self):
        self.object.save_data()


class MessageSplitter:
    @staticmethod
    def split_response(response):
        parts = response.split("```")
        response_list = []

        is_code_block = True
        response = ""
        for part in parts:
            is_code_block = not is_code_block
            index = 0
            if is_code_block:
                response += "```"
            while index < len(part):
                next_index = index + MESSAGE_LENGTH_LIMIT - len(response)
                response += part[index: next_index]
                index = next_index
                if len(response) >= MESSAGE_LENGTH_LIMIT:
                    if is_code_block:
                        response += "```"
                    response_list.append(response)
                    if is_code_block:
                        response = "```"
                    else:
                        response = ""
            if is_code_block:
                response += "```"
        response_list.append(response)
        return response_list

    """
    @staticmethod
    def find_triple_backticks_indices(text):
        indices = []
        i = 0
        while i < len(text) - 2:
            if text[i:i+3] == '```':
                indices.append(i)
                i += 3
            else:
                i += 1
        return indices

    @staticmethod
    def split_response(response):
        # Start a new message for coding blocks (Discord would display as if they were the same message), handle ``` in the middle of a message
        response_list = []
        index_list = MessageSplitter.find_triple_backticks_indices(response)

        is_code_block = False
        index = 0
        for end_index in index_list:
            start_with_code_block = False
            while index < end_index:
                temp_response = "```" if start_with_code_block else ""
                start_with_code_block = False
                next_index = index + MESSAGE_LENGTH_LIMIT
                if next_index < end_index:
                    if is_code_block:
                        temp_response += response[index:next_index] + "```"
                        start_with_code_block = True
                    else:
                        temp_response += response[index:next_index]
                else:
                    next_index = end_index + 3 if is_code_block else end_index
                    temp_response += response[index : next_index]
                response_list.append(temp_response)
                index = next_index
            is_code_block = not is_code_block
        response_list.append(response[index:])
        return response_list
    """
