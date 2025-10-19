from sqlalchemy import desc, func
from .models import AdvancedUser, AdvancedGame, AdvancedInventory, AdvancedMarket, GameHistory
from .db_manager import db_manager

class AdvancedQueries:
    @staticmethod
    def get_top_players(limit=10):
        session = db_manager.get_session()
        try:
            return session.query(AdvancedUser).order_by(
                desc(AdvancedUser.level),
                desc(AdvancedUser.coins)
            ).limit(limit).all()
        finally:
            session.close()
    
    @staticmethod
    def get_user_inventory(user_id):
        session = db_manager.get_session()
        try:
            return session.query(AdvancedInventory).filter(
                AdvancedInventory.user_id == user_id,
                AdvancedInventory.quantity > 0
            ).all()
        finally:
            session.close()
    
    @staticmethod
    def get_market_listings(limit=20):
        session = db_manager.get_session()
        try:
            return session.query(AdvancedMarket).filter(
                AdvancedMarket.sold == False
            ).order_by(AdvancedMarket.listed_at.desc()).limit(limit).all()
        finally:
            session.close()
    
    @staticmethod
    def update_game_state(game_id, state, additional_data=None):
        session = db_manager.get_session()
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
    
    @staticmethod
    def update_game_teams(game_id, teams_data):
        session = db_manager.get_session()
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
    
    @staticmethod  
    def add_to_inventory(user_id, item_name, quantity):
        session = db_manager.get_session()
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
    
    @staticmethod
    def remove_from_inventory(user_id, item_name, quantity):
        session = db_manager.get_session()
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
    
    @staticmethod
    def add_market_listing(seller_id, seller_name, item_name, quantity, price):
        session = db_manager.get_session()
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

# Add these methods to db_manager
def get_top_players(limit=10):
    return AdvancedQueries.get_top_players(limit)

def get_user_inventory(user_id):
    return AdvancedQueries.get_user_inventory(user_id)

def get_market_listings(limit=20):
    return AdvancedQueries.get_market_listings(limit)

def update_game_state(game_id, state, additional_data=None):
    return AdvancedQueries.update_game_state(game_id, state, additional_data)

def update_game_teams(game_id, teams_data):
    return AdvancedQueries.update_game_teams(game_id, teams_data)

def add_to_inventory(user_id, item_name, quantity):
    return AdvancedQueries.add_to_inventory(user_id, item_name, quantity)

def remove_from_inventory(user_id, item_name, quantity):
    return AdvancedQueries.remove_from_inventory(user_id, item_name, quantity)

def add_market_listing(seller_id, seller_name, item_name, quantity, price):
    return AdvancedQueries.add_market_listing(seller_id, seller_name, item_name, quantity, price)
