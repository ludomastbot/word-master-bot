from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL, SHOP_ITEMS
from .models import Base, AdvancedUser, AdvancedGame, AdvancedInventory, AdvancedMarket, GameHistory, WordPack, Settings
from datetime import datetime

class AdvancedDatabaseManager:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        return self.Session()
    
    def create_user(self, user_id, username, first_name, last_name=""):
        session = self.get_session()
        try:
            user = AdvancedUser(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                referral_code=f"REF{user_id}"
            )
            session.add(user)
            session.commit()
            return user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_user(self, user_id):
        session = self.get_session()
        try:
            return session.query(AdvancedUser).filter(AdvancedUser.user_id == user_id).first()
        finally:
            session.close()
    
    def update_user_coins(self, user_id, coins_change):
        session = self.get_session()
        try:
            user = session.query(AdvancedUser).filter(AdvancedUser.user_id == user_id).first()
            if user:
                user.coins += coins_change
                if coins_change > 0:
                    user.total_coins_earned += coins_change
                session.commit()
            return user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update_user_daily(self, user_id, coins_earned, streak, last_daily):
        session = self.get_session()
        try:
            user = session.query(AdvancedUser).filter(AdvancedUser.user_id == user_id).first()
            if user:
                user.coins += coins_earned
                user.total_coins_earned += coins_earned
                user.daily_streak = streak
                user.last_daily = last_daily
                session.commit()
            return user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update_user_game_stats(self, user_id, coins_earned, xp_earned, won=False):
        session = self.get_session()
        try:
            user = session.query(AdvancedUser).filter(AdvancedUser.user_id == user_id).first()
            if user:
                user.coins += coins_earned
                user.total_coins_earned += coins_earned
                user.xp += xp_earned
                user.games_played += 1
                if won:
                    user.games_won += 1
                
                # Level up check
                while user.xp >= user.level * 100:
                    user.xp -= user.level * 100
                    user.level += 1
                
                session.commit()
            return user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def create_game(self, game_data):
        session = self.get_session()
        try:
            game = AdvancedGame(**game_data)
            session.add(game)
            session.commit()
            return game
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_active_game(self, chat_id):
        session = self.get_session()
        try:
            return session.query(AdvancedGame).filter(
                AdvancedGame.chat_id == chat_id,
                AdvancedGame.state.in_(['waiting', 'started'])
            ).first()
        finally:
            session.close()
    
    def update_game_state(self, game_id, state, additional_data=None):
        session = self.get_session()
        try:
            game = session.query(AdvancedGame).filter(AdvancedGame.id == game_id).first()
            if game:
                game.state = state
                if additional_data:
                    for key, value in additional_data.items():
                        setattr(game, key, value)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update_game_teams(self, game_id, teams_data):
        session = self.get_session()
        try:
            game = session.query(AdvancedGame).filter(AdvancedGame.id == game_id).first()
            if game:
                game.teams = teams_data
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update_game_turn(self, game_id, current_turn):
        session = self.get_session()
        try:
            game = session.query(AdvancedGame).filter(AdvancedGame.id == game_id).first()
            if game:
                game.current_turn = current_turn
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_top_players(self, limit=10):
        session = self.get_session()
        try:
            return session.query(AdvancedUser).order_by(
                desc(AdvancedUser.level),
                desc(AdvancedUser.coins)
            ).limit(limit).all()
        finally:
            session.close()
    
    def get_top_players_by_coins(self, limit=10):
        session = self.get_session()
        try:
            return session.query(AdvancedUser).order_by(
                desc(AdvancedUser.coins)
            ).limit(limit).all()
        finally:
            session.close()
    
    def get_top_players_by_wins(self, limit=10):
        session = self.get_session()
        try:
            return session.query(AdvancedUser).order_by(
                desc(AdvancedUser.games_won)
            ).limit(limit).all()
        finally:
            session.close()
    
    def get_user_inventory(self, user_id):
        session = self.get_session()
        try:
            return session.query(AdvancedInventory).filter(
                AdvancedInventory.user_id == user_id,
                AdvancedInventory.quantity > 0
            ).all()
        finally:
            session.close()
    
    def get_market_listings(self, limit=20):
        session = self.get_session()
        try:
            return session.query(AdvancedMarket).filter(
                AdvancedMarket.sold == False
            ).order_by(AdvancedMarket.listed_at.desc()).limit(limit).all()
        finally:
            session.close()
    
    def add_to_inventory(self, user_id, item_name, quantity):
        session = self.get_session()
        try:
            # Check if item already exists
            existing = session.query(AdvancedInventory).filter(
                AdvancedInventory.user_id == user_id,
                AdvancedInventory.item_name == item_name
            ).first()
            
            if existing:
                existing.quantity += quantity
            else:
                new_item = AdvancedInventory(
                    user_id=user_id,
                    item_name=item_name,
                    quantity=quantity
                )
                session.add(new_item)
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def remove_from_inventory(self, user_id, item_name, quantity):
        session = self.get_session()
        try:
            item = session.query(AdvancedInventory).filter(
                AdvancedInventory.user_id == user_id,
                AdvancedInventory.item_name == item_name
            ).first()
            
            if item and item.quantity >= quantity:
                item.quantity -= quantity
                if item.quantity == 0:
                    session.delete(item)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_market_listing(self, seller_id, seller_name, item_name, quantity, price):
        session = self.get_session()
        try:
            listing = AdvancedMarket(
                item_name=item_name,
                seller_id=seller_id,
                seller_name=seller_name,
                quantity=quantity,
                price=price,
                item_type=SHOP_ITEMS.get(item_name, {}).get('type', 'general')
            )
            session.add(listing)
            session.commit()
            return listing.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

# Global database instance
db_manager = AdvancedDatabaseManager()
