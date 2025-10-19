from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import TEAM_COLORS, SHOP_ITEMS

async def advanced_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    welcome_text = f"""
🌟 *Welcome to Advanced Word Master Bot* 🌟

👤 *User:* {user.mention_html()}
🎯 *Level:* 1 | ⚡ *XP:* 0/100
💰 *Coins:* 500 | 💎 *Gems:* 0

*🎮 ADVANCED GAME MODES:*

*🧠 MEDCODI GAMES:*
• 2 Teams: Emoji, Classic, Black, Crazy, SuperCrazy, Insane, Adventure
• 3 Teams: Classic, Emoji, Crazy, SuperCrazy, Insane  
• 4 Teams: Classic, Emoji

*📚 KNOWLEDGE:*
• AI Dictionary - /ud word
• Image Quiz - /quiz_image
• Grammar Quiz - /grammar_quiz

*💰 ECONOMY:*
• Daily Bonus - /daily
• Shop System - /shop
• Market Trading - /market
• Inventory - /inventory

*⚙️ SETTINGS:*
• Game Settings - /settings
• Language - /language
• Word Packs - /wordpack

Use /help for detailed commands!
    """
    
    keyboard = [
        [InlineKeyboardButton("🎮 Quick Play", callback_data="quick_play"),
         InlineKeyboardButton("🛍️ Shop", callback_data="shop_main")],
        [InlineKeyboardButton("📊 Stats", callback_data="user_stats"),
         InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings_main"),
         InlineKeyboardButton("❓ Help", callback_data="help_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(welcome_text, reply_markup=reply_markup)

async def advanced_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
*🤖 ADVANCED WORD MASTER - COMMAND LIST*

*🎮 MEDCODI GAMES:*
`/medcodi_two_emoji` - 2 Team Emoji Mode
`/medcodi_two` - 2 Team Classic  
`/medcodi_two_black` - 2 Team Black Mode
`/medcodi_two_supercrazy` - 2 Team SuperCrazy
`/medcodi_two_crazy` - 2 Team Crazy
`/medcodi_two_insane` - 2 Team Insane
`/medcodi_two_adventure` - 2 Team Adventure
`/medcodi_triple_classic` - 3 Team Classic
`/medcodi_triple_emoji` - 3 Team Emoji
`/medcodi_triple_crazy` - 3 Team Crazy
`/medcodi_triple_supercrazy` - 3 Team SuperCrazy
`/medcodi_triple_insane` - 3 Team Insane
`/medcodi_four_classic` - 4 Team Classic
`/medcodi_four_emoji` - 4 Team Emoji
`/medcodi_random` - Random Mode

*📚 KNOWLEDGE COMMANDS:*
`/ud word` - AI Dictionary
`/define word` - Word Definition
`/quiz_image` - Image Quiz
`/grammar_quiz` - Grammar Quiz
`/quick_quiz` - Quick Quiz

*💰 ECONOMY COMMANDS:*
`/daily` - Daily Bonus
`/pay @user amount` - Pay Coins
`/transfer @user amount` - Transfer
`/donate amount` - Donate to Bot
`/shop` - Open Shop
`/buy item quantity` - Buy Items
`/sell item quantity price` - Sell in Market
`/gift @user item quantity` - Gift Items
`/inventory` - Your Inventory
`/market` - Player Market

*📊 STATS COMMANDS:*
`/stats` - Your Statistics
`/profile` - Detailed Profile
`/leaderboard` - Top Players
`/top` - Various Leaderboards

*⚙️ SETTINGS COMMANDS:*
`/settings` - Game Settings
`/time minutes` - Set Turn Time
`/language` - Change Language
`/wordpack` - Manage Word Packs

*🎯 GAME CONTROLS:*
`/skip` - Skip Turn
`/card word` - Guess Card
`/medcodi_end` - End Game

*Type any command to get started!*
    """
    
    await update.message.reply_markdown(help_text)

async def bot_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_text = """
*🤖 ADVANCED WORD MASTER BOT*

*Version:* 3.0 Advanced
*Developer:* Your Name
*Platform:* Telegram

*✨ FEATURES:*
• 🤖 AI-Powered Dictionary
• 🎮 15+ Medcodi Game Modes
• 💰 Advanced Economy System
• 🛍️ Dynamic Shop & Market
• 📊 Player Statistics & Levels
• 🌐 Multi-Language Support
• ⚡ Real-time Gameplay
• 🏆 Achievement System

*🔧 TECHNICAL:*
• Built with python-telegram-bot
• SQLite Database
• PIL Image Generation
• Async Operations
• Rate Limiting
• Error Handling

*Support:* @yourchannel
    """
    
    await update.message.reply_markdown(info_text)
