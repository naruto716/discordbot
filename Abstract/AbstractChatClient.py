from abc import ABC, abstractmethod


class AbstractChatClient(ABC):
    @abstractmethod
    async def on_ready(self):
        pass

    @abstractmethod
    async def on_message(self, message):
        pass
