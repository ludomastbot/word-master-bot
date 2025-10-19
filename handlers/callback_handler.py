from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_manager import db_manager
from config import TEAM_COLORS, SHOP_ITEMS, GAME_MODES
import random

async def advanced_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = query.from_user
    chat_id = query.message.chat_id
    
    # Handle different callback types
    if data.startswith('join_'):
        await handle_join_callback(query, context, data, user, chat_id)
    elif data.startswith('shop_'):
        await handle_shop_callback(query, context, data, user)
    elif data.startswith('game_'):
        await handle_game_callback(query, context, data, user, chat_id)
    elif data == 'quick_play':
        await handle_quick_play(query, context, user, chat_id)
    elif data == 'shop_main':
        await show_shop_menu(query, context, user)
    elif data == 'user_stats':
        await show_user_stats(query, context, user)
    elif data == 'leaderboard':
        await show_leaderboard(query, context, user)
    elif data == 'settings_main':
        await show_settings_menu(query, context, user, chat_id)
    elif data == 'help_main':
        await show_help_menu(query, context)

async def handle_join_callback(query, context, data, user, chat_id):
    game = db_manager.get_active_game(chat_id)
    if not game:
        await query.edit_message_text("❌ No active game found in this chat.")
        return
    
    action, role, team_name = data.split('_')
    username = user.username or user.first_name
    
    # Remove user from all teams first
    for team in game.teams.values():
        if team['spy'] == username:
            team['spy'] = None
        if username in team['guessers']:
            team['guessers'].remove(username)
    
    # Add to new position
    if role == 'spy':
        if game.teams[team_name]['spy'] is None:
            game.teams[team_name]['spy'] = username
            await query.edit_message_text(f"✅ {username} joined as {team_name} team spy!")
        else:
            await query.answer("❌ Spy position already taken!", show_alert=True)
    elif role == 'guesser':
        if username not in game.teams[team_name]['guessers']:
            game.teams[team_name]['guessers'].append(username)
            await query.edit_message_text(f"✅ {username} joined as {team_name} team guesser!")
        else:
            await query.answer("❌ Already in this team!", show_alert=True)
    
    # Update game in database
    db_manager.update_game_teams(game.id, game.teams)
    await update_game_lobby(query, context, game)

async def handle_shop_callback(query, context, data, user):
    if data == 'shop_food':
        await show_shop_category(query, context, user, 'food')
    elif data == 'shop_love':
        await show_shop_category(query, context, user, 'love')
    elif data == 'shop_premium':
        await show_shop_category(query, context, user, 'premium')
    elif data.startswith('buy_'):
        item_name = data.replace('buy_', '')
        await handle_buy_item(query, context, user, item_name)

async def handle_game_callback(query, context, data, user, chat_id):
    if data == 'begin_game':
        game = db_manager.get_active_game(chat_id)
        if game and game.creator_id == user.id:
            # Check if all teams have at least spy and one guesser
            can_start = True
            for team_name, team_data in game.teams.items():
                if not team_data['spy'] or len(team_data['guessers']) == 0:
                    can_start = False
                    break
            
            if can_start:
                await start_medcodi_game(query, context, game)
            else:
                await query.answer("❌ All teams need at least 1 spy and 1 guesser!", show_alert=True)
        else:
            await query.answer("❌ Only game creator can start the game!", show_alert=True)

async def handle_quick_play(query, context, user, chat_id):
    # Random game mode for quick play
    mode = random.choice(['two_emoji', 'two_classic', 'triple_classic'])
    from handlers.medcodi_handler import create_advanced_medcodi_game
    
    # Simulate command
    context.args = []
    update = Update(update_id=0, message=query.message)
    await create_advanced_medcodi_game(update, context)

async def show_shop_menu(query, context, user):
    shop_text = """
🛍️ *ADVANCED SHOP SYSTEM*

💰 *Your Balance:* 500 coins
💎 *Gems:* 0

*Categories:*
• 🍕 Food Items
• 💝 Love Items  
• 👑 Premium Items
• 📊 Your Inventory

*Use buttons below to browse!*
    """
    
    keyboard = [
        [InlineKeyboardButton("🍕 Food", callback_data="shop_food"),
         InlineKeyboardButton("💝 Love", callback_data="shop_love")],
        [InlineKeyboardButton("👑 Premium", callback_data="shop_premium"),
         InlineKeyboardButton("📦 Inventory", callback_data="inventory_view")],
        [InlineKeyboardButton("💰 Market", callback_data="market_view"),
         InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(shop_text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_shop_category(query, context, user, category):
    items = {k:v for k,v in SHOP_ITEMS.items() if v['type'] == category}
    category_name = category.title()
    
    shop_text = f"🛍️ *{category_name} Shop*\n\n"
    
    for item_name, item_data in items.items():
        shop_text += f"{item_data['emoji']} *{item_name.replace('_', ' ').title()}* - {item_data['price']} coins\n"
    
    keyboard = []
    for item_name in items.keys():
        keyboard.append([InlineKeyboardButton(
            f"Buy {item_name.replace('_', ' ').title()}",
            callback_data=f"buy_{item_name}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Back to Shop", callback_data="shop_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(shop_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_buy_item(query, context, user, item_name):
    user_data = db_manager.get_user(user.id)
    item_data = SHOP_ITEMS.get(item_name)
    
    if not item_data:
        await query.answer("❌ Item not found!", show_alert=True)
        return
    
    if user_data.coins >= item_data['price']:
        # Process purchase
        db_manager.update_user_coins(user.id, -item_data['price'])
        db_manager.add_to_inventory(user.id, item_name, 1)
        
        await query.answer(f"✅ Purchased {item_name} for {item_data['price']} coins!", show_alert=True)
        await show_shop_menu(query, context, user)
    else:
        await query.answer("❌ Not enough coins!", show_alert=True)

async def show_user_stats(query, context, user):
    user_data = db_manager.get_user(user.id)
    if not user_data:
        user_data = db_manager.create_user(user.id, user.username, user.first_name, user.last_name)
    
    stats_text = f"""
📊 *ADVANCED STATISTICS*

👤 *Player:* {user.first_name}
🎯 *Level:* {user_data.level} | ⚡ *XP:* {user_data.xp}/1000
💰 *Coins:* {user_data.coins} | 💎 *Gems:* {user_data.gems}

*🎮 Game Stats:*
• Games Played: {user_data.games_played}
• Games Won: {user_data.games_won}
• Win Rate: {((user_data.games_won/user_data.games_played)*100) if user_data.games_played > 0 else 0:.1f}%
• Total Coins Earned: {user_data.total_coins_earned}

*📈 Activity:*
• Daily Streak: {user_data.daily_streak} days
• Referral Code: {user_data.referral_code}
    """
    
    keyboard = [
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
         InlineKeyboardButton("🛍️ Shop", callback_data="shop_main")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_leaderboard(query, context, user):
    top_players = db_manager.get_top_players(10)
    
    leaderboard_text = "🏆 *ADVANCED LEADERBOARD*\n\n"
    
    for i, player in enumerate(top_players, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        leaderboard_text += f"{medal} {player.first_name} - Lvl {player.level} | {player.coins} coins\n"
    
    keyboard = [
        [InlineKeyboardButton("📊 My Stats", callback_data="user_stats"),
         InlineKeyboardButton("🎮 Quick Play", callback_data="quick_play")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(leaderboard_text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_settings_menu(query, context, user, chat_id):
    settings_text = """
⚙️ *ADVANCED SETTINGS*

*Game Settings:*
• Turn Time: 6 minutes
• Max Players: 10
• Language: English

*Bot Settings:*
• Coin System: Enabled
• Auto Start: Disabled
• Notifications: Enabled

*Use buttons to modify settings!*
    """
    
    keyboard = [
        [InlineKeyboardButton("⏰ Turn Time", callback_data="set_time"),
         InlineKeyboardButton("👥 Max Players", callback_data="set_players")],
        [InlineKeyboardButton("🌐 Language", callback_data="set_language"),
         InlineKeyboardButton("🎴 Word Packs", callback_data="wordpacks")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(settings_text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_help_menu(query, context):
    help_text = """
❓ *ADVANCED HELP*

*Quick Start:*
1. Use /medcodi_two to start a game
2. Players join using buttons
3. Click Begin Game when ready
4. Follow on-screen instructions

*Need Help?*
• Use /help for full command list
• Contact support for issues
• Check /tutorial for guides

*Pro Tips:*
• Use /daily for free coins
• Trade items in /market
• Level up for rewards
    """
    
    keyboard = [
        [InlineKeyboardButton("📚 Commands", callback_data="full_commands"),
         InlineKeyboardButton("🎮 Tutorial", callback_data="tutorial")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')

async def update_game_lobby(query, context, game):
    # Update the game lobby message with current player list
    from handlers.medcodi_handler import send_game_lobby
    await send_game_lobby(query, context, game, game.mode)

async def start_medcodi_game(query, context, game):
    from games.medcodi.game_manager import AdvancedMedcodiGame
    game_manager = AdvancedMedcodiGame(game)
    await game_manager.start_game(query, context)
