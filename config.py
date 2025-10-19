import os

BOT_TOKEN = "8354233939:AAFwq_8VbCYhWRYeeKqqZERiRh8dOLFW7Ag"
ADMIN_IDS = [123456789]  # Your Telegram ID yahan dalo

# Advanced Database
DATABASE_URL = "sqlite:///word_master.db"

# Advanced Game Settings
DEFAULT_TURN_TIME = 360
MAX_PLAYERS_PER_TEAM = 15
MAX_GUESSERS = 12
HINT_TIME_LIMIT = 240  # 4 minutes for spy

# Advanced Team System
TEAM_COLORS = {
    "red": {"emoji": "❤️", "hex": "#FF0000"},
    "pink": {"emoji": "🩷", "hex": "#FF69B4"}, 
    "orange": {"emoji": "🧡", "hex": "#FFA500"},
    "grey": {"emoji": "🩶", "hex": "#808080"},
    "yellow": {"emoji": "💛", "hex": "#FFFF00"},
    "green": {"emoji": "💚", "hex": "#00FF00"},
    "blue": {"emoji": "💙", "hex": "#0000FF"},
    "maple": {"emoji": "🍁", "hex": "#D2691E"},
    "mud": {"emoji": "🪹", "hex": "#8B4513"},
    "yellowish": {"emoji": "🔰", "hex": "#9ACD32"}
}

# Advanced Coin Economy - YAHAN WIN_COINS ADD KARO
DAILY_COINS = 200
WIN_COINS = 50  # ADD THIS LINE
LOSE_COINS = 20
QUIZ_COINS = 30
GRAMMAR_COINS = 25
REFERRAL_COINS = 100
WIN_COINS_MULTIPLIER = 2  # ADD THIS LINE

# Advanced Shop System
SHOP_ITEMS = {
    "pizza": {"price": 150, "type": "food", "emoji": "🍕", "effect": "health"},
    "burger": {"price": 100, "type": "food", "emoji": "🍔", "effect": "health"},
    "coke": {"price": 50, "type": "food", "emoji": "🥤", "effect": "energy"},
    "chocolate": {"price": 80, "type": "food", "emoji": "🍫", "effect": "mood"},
    "icecream": {"price": 70, "type": "food", "emoji": "🍦", "effect": "mood"},
    "rose": {"price": 200, "type": "love", "emoji": "🌹", "effect": "romance"},
    "diamond_ring": {"price": 1000, "type": "love", "emoji": "💍", "effect": "romance"},
    "teddy_bear": {"price": 300, "type": "love", "emoji": "🧸", "effect": "affection"},
    "perfume": {"price": 400, "type": "love", "emoji": "🌸", "effect": "attraction"},
    "love_letter": {"price": 150, "type": "love", "emoji": "💌", "effect": "emotion"},
    "gold_bar": {"price": 5000, "type": "premium", "emoji": "🪙", "effect": "investment"},
    "crown": {"price": 3000, "type": "premium", "emoji": "👑", "effect": "prestige"}
}

# Advanced Game Modes
GAME_MODES = {
    "two_emoji": {"teams": 2, "type": "emoji", "cards": [9, 8, 1, 6]},
    "two_classic": {"teams": 2, "type": "classic", "cards": [9, 8, 1, 6]},
    "two_black": {"teams": 2, "type": "black", "cards": [9, 8, 1, 6]},
    "two_supercrazy": {"teams": 2, "type": "supercrazy", "cards": [9, 8, 1, 6]},
    "two_crazy": {"teams": 2, "type": "crazy", "cards": [9, 8, 1, 6]},
    "two_insane": {"teams": 2, "type": "insane", "cards": [9, 8, 1, 6]},
    "two_adventure": {"teams": 2, "type": "adventure", "cards": [9, 8, 1, 6]},
    "triple_classic": {"teams": 3, "type": "classic", "cards": [8, 7, 6, 3]},
    "triple_emoji": {"teams": 3, "type": "emoji", "cards": [8, 7, 6, 3]},
    "triple_crazy": {"teams": 3, "type": "crazy", "cards": [8, 7, 6, 3]},
    "triple_supercrazy": {"teams": 3, "type": "supercrazy", "cards": [8, 7, 6, 3]},
    "triple_insane": {"teams": 3, "type": "insane", "cards": [8, 7, 6, 3]},
    "four_classic": {"teams": 4, "type": "classic", "cards": [6, 6, 5, 5, 2]},
    "four_emoji": {"teams": 4, "type": "emoji", "cards": [6, 6, 5, 5, 2]}
}

# AI Dictionary Settings
AI_DICTIONARY_APIS = {
    "urban": "https://api.urbandictionary.com/v0/define?term={}",
    "wiki": "https://en.wikipedia.org/api/rest_v1/page/summary/{}",
    "google": "https://api.dictionaryapi.dev/api/v2/entries/en/{}"
}

# Advanced Security
MAX_GAMES_PER_GROUP = 3
RATE_LIMIT = 10  # messages per minute
BLACKLIST_WORDS = ["hack", "spam", "cheat"]
