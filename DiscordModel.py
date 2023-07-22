from Abstract.AbstractModel import AbstractModel
from ChatBots.ChatBotFactory import ChatBotFactory
from Abstract.AbstractChatBot import ChatBotAbstract, ChatBotStreamableAbstract
from ModelEvent import *
from queue import Queue
import threading
import asyncio
from PermissionManager import PermissionManager
from BotTypes import BOT_TYPES
import pickle
from Config import *


class MessagePair:
    def __init__(self, message_author, message, reply=None):
        self.message = message
        self.reply = reply
        self.message_author = message_author
        self.mutex = threading.Lock()

    def get_message(self):
        with self.mutex:
            return self.message

    def get_reply(self):
        with self.mutex:
            return self.reply

    def set_message(self, message):
        with self.mutex:
            self.message = message

    def set_reply(self, reply):
        with self.mutex:
            self.reply = reply

    def get_message_author(self):
        with self.mutex:
            return self.message_author

    def set_message_author(self, message_author):
        with self.mutex:
            self.message_author = message_author

    def __getstate__(self):
        # Copy the object's state without the lock
        state = self.__dict__.copy()
        del state['mutex']
        return state

    def __setstate__(self, state):
        # Restore the object's state and create a new lock
        self.__dict__.update(state)
        self.mutex = threading.Lock()


class Context:
    # One context for each channel
    def __init__(self, context_id, system_prompt=None):
        self.message_context_id = context_id
        self.system_prompt = system_prompt
        self.context = list()

        # extra
        self.active_session = dict()

    def get_context_id(self):
        return self.message_context_id

    def get_system_prompt(self):
        return self.system_prompt

    def get_context(self):
        """
        return:
        [
          {
            "role": "system",
            "content": "You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible.\nKnowledge cutoff: 2021-09-01\nCurrent date: 2023-03-02"
          },
          {
            "role": "user",
            "content": "How are you?"
          },
          {
            "role": "assistant",
            "content": "I am doing well"
          },
          {
            "role": "user",
            "content": "How long does light take to travel from the sun to the earth?"
          }
        ]
        """

        context_list = list()
        if self.system_prompt is not None:
            context_list.append({"role": "system", "content": self.system_prompt})
        for message_pair in self.context:
            message = message_pair.get_message()
            reply = message_pair.get_reply()
            if message is not None:
                context_list.append({"role": "user", "content": message})
            if reply is not None:
                context_list.append({"role": "assistant", "content": reply})
        return context_list

    def add_message_pair(self, message_pair):
        self.context.append(message_pair)

    def add_message_pair(self, message, message_author, reply=None):
        message_pair = MessagePair(message_author, message, reply)
        self.context.append(message_pair)
        return message_pair

    def get_raw_context(self):
        return self.context

    # extra
    def get_session(self, session_name):
        if session_name in self.active_session:
            return self.active_session[session_name]
        else:
            return None

    def set_session(self, session_name, session):
        self.active_session[session_name] = session

    def remove_session(self, session_name):
        if session_name in self.active_session:
            del self.active_session[session_name]

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['active_session']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.active_session = dict()


class DataStorage:
    def __init__(self, data_filename):
        self._data_filename = data_filename
        if data_filename is not None:
            try:
                self.load_data()
                return
            except Exception:
                pass
        self.message_logs = dict()
        self.engine_logs = dict()
        self.non_stream_users = list()
        self.own_context_users = list()
        self.permission_manager = PermissionManager()

    def save_data(self):
        with open(self._data_filename, 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    def load_data(self):
        with open(self._data_filename, 'rb') as input_file:
            data = pickle.load(input_file)
            self.message_logs = data.message_logs
            self.engine_logs = data.engine_logs
            self.non_stream_users = data.non_stream_users
            self.own_context_users = data.own_context_users
            self.permission_manager = data.permission_manager


class Data:
    def __init__(self, data_filename=None):
        self._data_storage = DataStorage(data_filename)
        self.message_logs = self._data_storage.message_logs
        self.engine_logs = self._data_storage.engine_logs
        self.non_stream_users = self._data_storage.non_stream_users
        self.own_context_users = self._data_storage.own_context_users
        self.permission_manager = self._data_storage.permission_manager
        self._data_filename = data_filename

    def get_context(self, context_id):
        if context_id not in self.message_logs:
            self.message_logs[context_id] = Context(context_id)
        return self.message_logs[context_id]

    def clear_context(self, context_id):
        del self.message_logs[context_id]

    def set_context(self, context_id, context: Context):
        self.message_logs[context_id] = context

    def set_engine_log(self, user, engine):  # create if not exists
        if engine in BOT_TYPES:
            needed_permission = BOT_TYPES[engine]["permission"]
            if self.permission_manager.check_permission(user, needed_permission):
                self.engine_logs[user] = engine
                return
        self.engine_logs[user] = "default"

    def get_engine_log(self, user) -> ChatBotAbstract:
        if user not in self.engine_logs:
            self.set_engine_log(user, "default")
        return ChatBotFactory.get_bot(self.engine_logs[user])

    def check_user_stream_mode(self, user):
        return user not in self.non_stream_users

    def toggle_user_stream_mode(self, user):
        # return True if stream mode, False if non-stream mode
        if user in self.non_stream_users:
            self.non_stream_users.remove(user)
            return True  # stream mode
        else:
            self.non_stream_users.append(user)
            return False  # non-stream mode

    def check_user_own_context(self, user):
        return user in self.own_context_users

    def toggle_user_own_context(self, user):
        # return True if own context, False if not own context
        if user in self.own_context_users:
            self.own_context_users.remove(user)
            return False
        else:
            self.own_context_users.append(user)
            return True

    def reset_context(self, context_id):
        if context_id in self.message_logs:
            del self.message_logs[context_id]
            return True
        else:
            return False

    def get_permission_manager(self):
        return self.permission_manager

    def save_data(self):
        self._data_storage.save_data()


class DiscordModel(AbstractModel):
    def __init__(self, discord_client):
        self.discord_client = discord_client
        self.data = Data(DATA_FILENAME)
        self.thread_pool = ThreadPool(100)  # max 100 threads
        self.next_clean_flag = True

    def process_message(self, message, message_content):
        context = self.data.get_context(message.author.id) if self.check_own_context(
            message) else self.data.get_context(message.channel.id)
        engine = self.data.get_engine_log(message.author.id)
        self.add_event(
            DiscordMessageStreamAIEvent(message, message_content, context, engine,
                                        self.discord_client)
            if self.check_stream_mode(message) and isinstance(engine, ChatBotStreamableAbstract) else
            DiscordMessageAIEvent(message, message_content, context, engine,
                                  self.discord_client)
        )

    def set_model(self, user, engine):
        self.data.set_engine_log(user, engine)

    def get_permission_manager(self):
        return self.data.get_permission_manager()

    def toggle_stream_mode(self, message):
        return self.data.toggle_user_stream_mode(message.author.id)

    def toggle_own_context(self, message):
        return self.data.toggle_user_own_context(message.author.id)

    async def save_data(self):
        while True:
            await asyncio.sleep(300)
            self.data.save_data()

    # utility functions
    def check_stream_mode(self, message):
        return self.data.check_user_stream_mode(message.author.id)

    def check_own_context(self, message):
        return self.data.check_user_own_context(message.author.id)

    def reset_context(self, message):
        if self.check_own_context(message):
            return self.data.reset_context(message.author.id)
        else:
            return self.data.reset_context(message.channel.id)

    def clean_redundant_threads(self):
        self.thread_pool.remove_redundant_threads()

    def add_event(self, event: ModelEvent):
        self.thread_pool.add_event(event)
        self.next_clean_flag = False

    async def clean_redundant_threads_loop(self):
        while True:
            await asyncio.sleep(600)
            if self.next_clean_flag:
                self.clean_redundant_threads()
            self.next_clean_flag = True


class ThreadPool:
    def __init__(self, max_num_threads):
        self.max_num_threads = max_num_threads
        self.event_queue = Queue()
        self.available_threads = 0
        self.total_threads = 0
        self.mutex = threading.Lock()

    def inc_available_threads(self):
        with self.mutex:
            self.available_threads += 1

    def dec_available_threads(self):
        with self.mutex:
            self.available_threads -= 1

    def add_event(self, event):
        self.event_queue.put(event)
        if self.available_threads == 0 and self.total_threads <= self.max_num_threads:
            self.total_threads += 1
            thread = ModelThread(self)
            thread.start()

    def remove_redundant_threads(self):
        for i in range(self.available_threads - 5):
            self.total_threads -= 1
            self.available_threads -= 1
            self.event_queue.put(ThreadTerminateEvent())


class ModelThread(threading.Thread):
    def __init__(self, thread_pool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.terminate_flag = threading.Event()
        self.thread_pool = thread_pool

    def run(self):
        while True:
            try:
                self.thread_pool.inc_available_threads()
                event = self.thread_pool.event_queue.get()
                if isinstance(event, ThreadTerminateEvent):
                    return
                self.thread_pool.dec_available_threads()
                event.process()
            except Exception as e:
                print(repr(e))
                return
