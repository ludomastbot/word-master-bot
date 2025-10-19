from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class AdvancedUser(Base):
    __tablename__ = 'advanced_users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, index=True)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    coins = Column(Integer, default=500)
    gems = Column(Integer, default=0)
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    games_played = Column(Integer, default=0)
    games_won = Column(Integer, default=0)
    total_coins_earned = Column(Integer, default=0)
    referral_code = Column(String(20), unique=True)
    referred_by = Column(Integer, default=0)
    daily_streak = Column(Integer, default=0)
    last_daily = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AdvancedGame(Base):
    __tablename__ = 'advanced_games'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, index=True)
    game_type = Column(String(50))
    mode = Column(String(50))
    state = Column(String(20), default='waiting')
    teams = Column(JSON)
    board = Column(JSON)
    current_turn = Column(String(20))
    hint = Column(JSON)
    revealed_cards = Column(JSON, default=[])
    turn_history = Column(JSON, default=[])
    settings = Column(JSON, default={})
    creator_id = Column(Integer)
    winner = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)

class AdvancedInventory(Base):
    __tablename__ = 'advanced_inventory'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    item_name = Column(String(100))
    quantity = Column(Integer, default=0)
    equipped = Column(Boolean, default=False)
    purchase_date = Column(DateTime, default=datetime.utcnow)

class AdvancedMarket(Base):
    __tablename__ = 'advanced_market'
    
    id = Column(Integer, primary_key=True)
    item_name = Column(String(100))
    seller_id = Column(Integer)
    seller_name = Column(String(100))
    quantity = Column(Integer)
    price = Column(Integer)
    item_type = Column(String(50))
    listed_at = Column(DateTime, default=datetime.utcnow)
    sold = Column(Boolean, default=False)
    sold_at = Column(DateTime)

class GameHistory(Base):
    __tablename__ = 'game_history'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer)
    user_id = Column(Integer)
    game_type = Column(String(50))
    result = Column(String(20))
    coins_earned = Column(Integer, default=0)
    xp_earned = Column(Integer, default=0)
    played_at = Column(DateTime, default=datetime.utcnow)

class WordPack(Base):
    __tablename__ = 'word_packs'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    language = Column(String(20), default='english')
    words = Column(JSON)
    created_by = Column(Integer)
    is_public = Column(Boolean, default=False)
    used_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Settings(Base):
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    language = Column(String(10), default='en')
    turn_time = Column(Integer, default=360)
    max_players = Column(Integer, default=10)
    enabled_games = Column(JSON, default=['medcodi', 'quiz', 'grammar'])
    auto_start = Column(Boolean, default=False)
    coin_system = Column(Boolean, default=True)
