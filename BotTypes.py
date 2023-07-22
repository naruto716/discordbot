from ChatBots.ChatGPTUnofficial import Gpt4Official, Gpt35Official
from ChatBots.Poe import *
from ChatBots.GoogleBard import *

DEFAULT_ENGINE = Gpt35Poe  # The default engine can always be used by users regardless of their permission

BOT_TYPES = {
    "gpt-3.5-p": {
        "description": "GPT3.5 (ChatGPT) Engine | Perm: 0",
        "class": Gpt35Poe,
        "permission": 0
    },
    "claude-p": {
        "description": "Claude Engine | Perm: 0",
        "class": ClaudePoe,
        "permission": 0
    },
    "google-palm-p": {
        "description": "Google Palm Engine | Perm: 0",
        "class": GooglePalmPoe,
        "permission": 0
    },
    "google-bard": {
        "description": "Google Bard Engine | Perm: 0 | Not sharing context with other engines",
        "class": GoogleBard,
        "permission": 0
    },
    "gpt-3.5-turbo": {
        "description": "Official GPT3.5 (ChatGPT) Engine | Perm: 1",
        "class": Gpt35Official,
        "permission": 1
    },
    "gpt-4-p": {
        "description": "Alternative GPT4 Engin | Perm: 1",
        "class": Gpt4Poe,
        "permission": 1
    },
    "claude-plus-p": {
        "description": "Claude+ Engine | Perm: 1",
        "class": ClaudePlusPoe,
        "permission": 1
    },
    "gpt-4": {
        "description": "Official GPT4 Engine | Perm: 2",
        "class": Gpt4Official,
        "permission": 2
    },
    "default": {
        "description": "Default Engine (ChatGPT) | Perm: 0",
        "class": DEFAULT_ENGINE,
        "permission": 0
    }
}