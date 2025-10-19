from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_manager import db_manager
from config import DEFAULT_TURN_TIME, MAX_PLAYERS_PER_TEAM

async def advanced_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    settings_text = """
⚙️ *ADVANCED BOT SETTINGS*

*Current Configuration:*
• ⏰ Turn Time: 6 minutes
• 👥 Max Players: 10 per team
• 🌐 Language: English
• 💰 Coin System: Enabled
• 🎮 Auto Start: Disabled

*Group Settings:*
• Game Notifications: Enabled
• Welcome Messages: Enabled
• Admin Only Commands: Disabled

*Use buttons below to modify settings!*
    """
    
    keyboard = [
        [InlineKeyboardButton("⏰ Turn Time", callback_data="settings_time"),
         InlineKeyboardButton("👥 Max Players", callback_data="settings_players")],
        [InlineKeyboardButton("🌐 Language", callback_data="settings_language"),
         InlineKeyboardButton("🎴 Word Packs", callback_data="settings_wordpacks")],
        [InlineKeyboardButton("💰 Economy", callback_data="settings_economy"),
         InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications")],
        [InlineKeyboardButton("🛡️ Security", callback_data="settings_security"),
         InlineKeyboardButton("🔧 Advanced", callback_data="settings_advanced")],
        [InlineKeyboardButton("🔄 Reset Defaults", callback_data="settings_reset"),
         InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_markdown(settings_text, reply_markup=reply_markup)

async def set_advanced_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("""
⏰ *Set Turn Time:* `/time minutes`
*Example:* `/time 5` (sets 5 minutes per turn)

*Recommended Times:*
• 3-5 minutes: Fast games
• 6-8 minutes: Standard games  
• 10+ minutes: Relaxed games
        """, parse_mode='Markdown')
        return
    
    try:
        minutes = int(context.args[0])
        if minutes < 1 or minutes > 30:
            await update.message.reply_text("❌ Time must be between 1 and 30 minutes!")
            return
        
        # Update settings (in real implementation, save to database)
        await update.message.reply_text(f"✅ Turn time set to {minutes} minutes!")
        
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number!")

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
         InlineKeyboardButton("🇮🇳 Hindi", callback_data="lang_hi")],
        [InlineKeyboardButton("🇪🇸 Spanish", callback_data="lang_es"),
         InlineKeyboardButton("🇫🇷 French", callback_data="lang_fr")],
        [InlineKeyboardButton("🔙 Back", callback_data="settings_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌐 *Select Language:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def advanced_wordpack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wordpack_text = """
🎴 *ADVANCED WORD PACK MANAGEMENT*

*Available Word Packs:*
• 📚 Default English (500+ words)
• 🎬 Movies & TV Shows
• 🌍 Countries & Cities  
• 🐾 Animals & Nature
• 🔬 Science & Technology
• 🎵 Music & Entertainment

*Features:*
• Create custom word packs
• Import/export word lists
• Share with friends
• Community word packs
        """
    
    keyboard = [
        [InlineKeyboardButton("📥 Import Pack", callback_data="wp_import"),
         InlineKeyboardButton("📤 Export Pack", callback_data="wp_export")],
        [InlineKeyboardButton("🆕 Create New", callback_data="wp_create"),
         InlineKeyboardButton("👥 Community", callback_data="wp_community")],
        [InlineKeyboardButton("⚙️ Manage Packs", callback_data="wp_manage"),
         InlineKeyboardButton("🔙 Back", callback_data="settings_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_markdown(wordpack_text, reply_markup=reply_markup)

async def handle_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    query = update.callback_query
    
    if data == "settings_time":
        keyboard = [
            [InlineKeyboardButton("3 minutes", callback_data="time_3"),
             InlineKeyboardButton("5 minutes", callback_data="time_5")],
            [InlineKeyboardButton("6 minutes", callback_data="time_6"),
             InlineKeyboardButton("8 minutes", callback_data="time_8")],
            [InlineKeyboardButton("10 minutes", callback_data="time_10"),
             InlineKeyboardButton("Custom", callback_data="time_custom")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⏰ *Select Turn Time:*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data.startswith("time_"):
        time_str = data.replace("time_", "")
        if time_str == "custom":
            await query.edit_message_text("💬 Please use `/time minutes` to set custom time.")
        else:
            minutes = int(time_str)
            await query.edit_message_text(f"✅ Turn time set to {minutes} minutes!")
    
    elif data == "settings_players":
        keyboard = [
            [InlineKeyboardButton("5 players", callback_data="players_5"),
             InlineKeyboardButton("8 players", callback_data="players_8")],
            [InlineKeyboardButton("10 players", callback_data="players_10"),
             InlineKeyboardButton("12 players", callback_data="players_12")],
            [InlineKeyboardButton("15 players", callback_data="players_15"),
             InlineKeyboardButton("20 players", callback_data="players_20")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "👥 *Set Maximum Players Per Team:*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data.startswith("players_"):
        players = int(data.replace("players_", ""))
        await query.edit_message_text(f"✅ Maximum players set to {players} per team!")
    
    elif data == "settings_language":
        await change_language_callback(query)
    
    elif data.startswith("lang_"):
        language = data.replace("lang_", "")
        language_names = {
            'en': 'English',
            'hi': 'Hindi', 
            'es': 'Spanish',
            'fr': 'French'
        }
        lang_name = language_names.get(language, 'English')
        await query.edit_message_text(f"✅ Language set to {lang_name}!")
    
    elif data == "settings_wordpacks":
        await advanced_wordpack_callback(query)
    
    elif data == "settings_main":
        await advanced_settings_callback(query)

async def change_language_callback(query):
    keyboard = [
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
         InlineKeyboardButton("🇮🇳 Hindi", callback_data="lang_hi")],
        [InlineKeyboardButton("🇪🇸 Spanish", callback_data="lang_es"),
         InlineKeyboardButton("🇫🇷 French", callback_data="lang_fr")],
        [InlineKeyboardButton("🔙 Back", callback_data="settings_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🌐 *Select Language:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def advanced_wordpack_callback(query):
    wordpack_text = """
🎴 *WORD PACK MANAGEMENT*

*Current Word Pack:* Default English
*Total Words:* 547 words
*Categories:* 12 categories

*Manage your word packs:*
        """
    
    keyboard = [
        [InlineKeyboardButton("📥 Import", callback_data="wp_import"),
         InlineKeyboardButton("📤 Export", callback_data="wp_export")],
        [InlineKeyboardButton("🆕 Create", callback_data="wp_create"),
         InlineKeyboardButton("🗑️ Delete", callback_data="wp_delete")],
        [InlineKeyboardButton("👥 Community", callback_data="wp_community"),
         InlineKeyboardButton("🔙 Back", callback_data="settings_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        wordpack_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def advanced_settings_callback(query):
    settings_text = """
⚙️ *ADVANCED BOT SETTINGS*

*Current Configuration:*
• ⏰ Turn Time: 6 minutes
• 👥 Max Players: 10 per team  
• 🌐 Language: English
• 💰 Coin System: Enabled
        """
    
    keyboard = [
        [InlineKeyboardButton("⏰ Turn Time", callback_data="settings_time"),
         InlineKeyboardButton("👥 Max Players", callback_data="settings_players")],
        [InlineKeyboardButton("🌐 Language", callback_data="settings_language"),
         InlineKeyboardButton("🎴 Word Packs", callback_data="settings_wordpacks")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        settings_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
