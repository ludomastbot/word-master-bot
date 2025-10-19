from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from database.db_manager import db_manager
from config import DAILY_COINS, REFERRAL_COINS, WIN_COINS, LOSE_COINS

async def advanced_daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db_manager.get_user(user.id)
    
    if not user_data:
        user_data = db_manager.create_user(user.id, user.username, user.first_name, user.last_name)
    
    now = datetime.utcnow()
    
    # Check if user already claimed daily bonus today
    if user_data.last_daily and user_data.last_daily.date() == now.date():
        await update.message.reply_text(
            f"❌ You already claimed your daily bonus today!\n"
            f"🕒 Next bonus available in {24 - now.hour} hours."
        )
        return
    
    # Calculate streak bonus
    streak_bonus = 0
    if user_data.last_daily and (user_data.last_daily.date() == (now.date() - timedelta(days=1))):
        user_data.daily_streak += 1
        streak_bonus = user_data.daily_streak * 10  # 10 extra coins per streak day
    else:
        user_data.daily_streak = 1
    
    total_coins = DAILY_COINS + streak_bonus
    
    # Update user data
    db_manager.update_user_daily(user.id, total_coins, user_data.daily_streak, now)
    
    bonus_text = f"""
🎉 *DAILY BONUS CLAIMED!*

💰 *Base Coins:* {DAILY_COINS}
🔥 *Streak Bonus:* {streak_bonus} coins (Day {user_data.daily_streak})
💰 *Total Received:* {total_coins} coins

📊 *New Balance:* {user_data.coins + total_coins} coins
🔥 *Current Streak:* {user_data.daily_streak} days

*Pro Tip:* Claim daily for increasing rewards! 🔥
    """
    
    keyboard = [
        [InlineKeyboardButton("🎮 Play Games", callback_data="quick_play"),
         InlineKeyboardButton("🛍️ Shop", callback_data="shop_main")],
        [InlineKeyboardButton("📊 Stats", callback_data="user_stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_markdown(bonus_text, reply_markup=reply_markup)

async def advanced_pay_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("""
💸 *Payment System:* `/pay @username amount`
*Example:* `/pay @john 100`

Transfer coins to other players!
        """, parse_mode='Markdown')
        return
    
    sender = update.effective_user
    recipient_username = context.args[0].replace('@', '')
    amount = int(context.args[1])
    
    sender_data = db_manager.get_user(sender.id)
    
    if not sender_data:
        sender_data = db_manager.create_user(sender.id, sender.username, sender.first_name)
    
    if sender_data.coins < amount:
        await update.message.reply_text(f"❌ Insufficient coins! You have {sender_data.coins} coins but trying to send {amount}.")
        return
    
    if amount < 1:
        await update.message.reply_text("❌ Amount must be at least 1 coin!")
        return
    
    # In real implementation, you'd lookup recipient by username
    # For demo, we'll assume recipient exists
    recipient_id = 123456789  # This should be actual user ID lookup
    
    # Process transfer
    db_manager.update_user_coins(sender.id, -amount)
    db_manager.update_user_coins(recipient_id, amount)
    
    await update.message.reply_text(
        f"✅ *Payment Sent Successfully!*\n\n"
        f"👤 *To:* @{recipient_username}\n"
        f"💰 *Amount:* {amount} coins\n"
        f"💳 *Your New Balance:* {sender_data.coins - amount} coins\n\n"
        f"*Transaction ID:* TX{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        parse_mode='Markdown'
    )

async def transfer_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await advanced_pay_coins(update, context)

async def donate_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("""
❤️ *Donation System:* `/donate amount`
*Example:* `/donate 50`

Donate coins to support bot development!
        """, parse_mode='Markdown')
        return
    
    user = update.effective_user
    amount = int(context.args[0])
    
    user_data = db_manager.get_user(user.id)
    
    if user_data.coins < amount:
        await update.message.reply_text(f"❌ Insufficient coins! You have {user_data.coins} coins.")
        return
    
    # Process donation (in real implementation, this would go to bot owner)
    db_manager.update_user_coins(user.id, -amount)
    
    await update.message.reply_text(
        f"❤️ *THANK YOU FOR YOUR DONATION!*\n\n"
        f"💰 *Amount:* {amount} coins\n"
        f"🙏 *From:* {user.first_name}\n"
        f"💳 *Your New Balance:* {user_data.coins - amount} coins\n\n"
        f"Your support helps improve the bot! 🚀",
        parse_mode='Markdown'
    )

async def advanced_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db_manager.get_user(user.id)
    
    if not user_data:
        user_data = db_manager.create_user(user.id, user.username, user.first_name, user.last_name)
    
    # Calculate additional stats
    win_rate = (user_data.games_won / user_data.games_played * 100) if user_data.games_played > 0 else 0
    coins_per_game = (user_data.total_coins_earned / user_data.games_played) if user_data.games_played > 0 else 0
    
    stats_text = f"""
📊 *ADVANCED PLAYER STATISTICS*

👤 *Player:* {user.first_name}
🆔 *User ID:* {user.id}
🎯 *Level:* {user_data.level} | ⚡ *XP:* {user_data.xp}/1000
💰 *Coins:* {user_data.coins} | 💎 *Gems:* {user_data.gems}

*🎮 Game Performance:*
• Games Played: {user_data.games_played}
• Games Won: {user_data.games_won}
• Win Rate: {win_rate:.1f}%
• Total Coins Earned: {user_data.total_coins_earned}
• Average Coins/Game: {coins_per_game:.1f}

*📈 Activity & Progress:*
• Daily Streak: {user_data.daily_streak} days
• Referral Code: `{user_data.referral_code}`
• Account Created: {user_data.created_at.strftime('%Y-%m-%d')}
• Last Active: {user_data.updated_at.strftime('%Y-%m-%d %H:%M')}

*🏆 Achievements:*
{'🥇 Master Player' if user_data.games_won >= 100 else '🎯 Rising Star' if user_data.games_won >= 50 else '🆕 New Player'}
{'💰 Coin Millionaire' if user_data.total_coins_earned >= 1000000 else '💸 Big Spender' if user_data.total_coins_earned >= 100000 else '💰 Coin Collector'}
    """
    
    keyboard = [
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
         InlineKeyboardButton("🛍️ Shop", callback_data="shop_main")],
        [InlineKeyboardButton("🎮 Quick Play", callback_data="quick_play"),
         InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_markdown(stats_text, reply_markup=reply_markup)

async def user_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await advanced_stats(update, context)

async def advanced_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_players = db_manager.get_top_players(15)
    
    leaderboard_text = "🏆 *ADVANCED LEADERBOARD*\n\n"
    
    for i, player in enumerate(top_players, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        leaderboard_text += f"{medal} *{player.first_name}* - Lvl {player.level} | {player.coins} coins | {player.games_won} wins\n"
    
    leaderboard_text += f"\n📊 *Total Players:* {len(top_players)}"
    leaderboard_text += f"\n⏰ *Updated:* {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC"
    
    keyboard = [
        [InlineKeyboardButton("💰 Richest Players", callback_data="lb_coins"),
         InlineKeyboardButton("🎮 Most Wins", callback_data="lb_wins")],
        [InlineKeyboardButton("📊 My Stats", callback_data="user_stats"),
         InlineKeyboardButton("🎮 Play Now", callback_data="quick_play")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_markdown(leaderboard_text, reply_markup=reply_markup)

async def top_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0] == 'coins':
        top_players = db_manager.get_top_players_by_coins(10)
        title = "💰 RICHEST PLAYERS"
    elif context.args and context.args[0] == 'wins':
        top_players = db_manager.get_top_players_by_wins(10)
        title = "🎮 MOST WINS"
    else:
        top_players = db_manager.get_top_players(10)
        title = "🏆 TOP PLAYERS"
    
    leaderboard_text = f"{title}\n\n"
    
    for i, player in enumerate(top_players, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        if title == "💰 RICHEST PLAYERS":
            leaderboard_text += f"{medal} *{player.first_name}* - {player.coins} coins\n"
        elif title == "🎮 MOST WINS":
            leaderboard_text += f"{medal} *{player.first_name}* - {player.games_won} wins\n"
        else:
            leaderboard_text += f"{medal} *{player.first_name}* - Lvl {player.level}\n"
    
    await update.message.reply_markdown(leaderboard_text)

# ADD THESE MISSING FUNCTIONS
def add_game_rewards(user_id, game_type, result, coins_earned, xp_earned=0):
    """Add rewards after game completion"""
    user_data = db_manager.get_user(user_id)
    if user_data:
        db_manager.update_user_game_stats(user_id, coins_earned, xp_earned, result == 'win')
        return user_data.level, user_data.xp
    return 0, 0

async def handle_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    query = update.callback_query
    
    if data == "user_stats":
        await show_user_stats_callback(query, context)
    elif data == "leaderboard":
        await show_leaderboard_callback(query, context)
    elif data == "lb_coins":
        await show_coin_leaderboard(query, context)
    elif data == "lb_wins":
        await show_wins_leaderboard(query, context)

async def show_user_stats_callback(query, context):
    user = query.from_user
    user_data = db_manager.get_user(user.id)
    
    if not user_data:
        user_data = db_manager.create_user(user.id, user.username, user.first_name, user.last_name)
    
    win_rate = (user_data.games_won / user_data.games_played * 100) if user_data.games_played > 0 else 0
    
    stats_text = f"""
📊 *PLAYER STATS*

👤 {user.first_name}
🎯 Level {user_data.level} | ⚡ {user_data.xp}/1000 XP
💰 {user_data.coins} coins

🎮 Games: {user_data.games_played} played, {user_data.games_won} won
📈 Win Rate: {win_rate:.1f}%
🔥 Daily Streak: {user_data.daily_streak} days
    """
    
    keyboard = [
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
         InlineKeyboardButton("🛍️ Shop", callback_data="shop_main")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_leaderboard_callback(query, context):
    top_players = db_manager.get_top_players(10)
    
    leaderboard_text = "🏆 *LEADERBOARD*\n\n"
    
    for i, player in enumerate(top_players, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        leaderboard_text += f"{medal} {player.first_name} - Lvl {player.level} | {player.coins} coins\n"
    
    keyboard = [
        [InlineKeyboardButton("💰 Richest", callback_data="lb_coins"),
         InlineKeyboardButton("🎮 Most Wins", callback_data="lb_wins")],
        [InlineKeyboardButton("📊 My Stats", callback_data="user_stats"),
         InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(leaderboard_text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_coin_leaderboard(query, context):
    top_players = db_manager.get_top_players_by_coins(10)
    
    leaderboard_text = "💰 *RICHEST PLAYERS*\n\n"
    
    for i, player in enumerate(top_players, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        leaderboard_text += f"{medal} {player.first_name} - {player.coins} coins\n"
    
    keyboard = [
        [InlineKeyboardButton("🏆 Overall", callback_data="leaderboard"),
         InlineKeyboardButton("🎮 Most Wins", callback_data="lb_wins")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(leaderboard_text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_wins_leaderboard(query, context):
    top_players = db_manager.get_top_players_by_wins(10)
    
    leaderboard_text = "🎮 *MOST WINS*\n\n"
    
    for i, player in enumerate(top_players, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        leaderboard_text += f"{medal} {player.first_name} - {player.games_won} wins\n"
    
    keyboard = [
        [InlineKeyboardButton("🏆 Overall", callback_data="leaderboard"),
         InlineKeyboardButton("💰 Richest", callback_data="lb_coins")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(leaderboard_text, reply_markup=reply_markup, parse_mode='Markdown')
