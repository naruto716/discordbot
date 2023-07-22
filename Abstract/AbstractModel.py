from abc import ABC, abstractmethod


class AbstractModel:
    @abstractmethod
    def process_message(self, message, message_content):
        pass
