from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_manager import db_manager
from config import TEAM_COLORS, GAME_MODES
import random

async def create_advanced_medcodi_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.split('@')[0] if '@' in update.message.text else update.message.text
    mode = command.replace('/', '').replace('medcodi_', '')
    
    if mode == "random":
        mode = random.choice(list(GAME_MODES.keys()))
    
    chat_id = update.effective_chat.id
    
    # Check if game already exists
    existing_game = db_manager.get_active_game(chat_id)
    if existing_game:
        await update.message.reply_text("🎮 A game is already running in this chat! Use /medcodi_end to end it first.")
        return
    
    # Create new game
    game_data = {
        "chat_id": chat_id,
        "game_type": "medcodi",
        "mode": mode,
        "state": "waiting",
        "creator_id": update.effective_user.id,
        "teams": initialize_teams(mode),
        "settings": {
            "turn_time": 360,
            "max_players": 10
        }
    }
    
    game = db_manager.create_game(game_data)
    await send_game_lobby(update, context, game, mode)

def initialize_teams(mode):
    game_config = GAME_MODES.get(mode, GAME_MODES["two_classic"])
    teams = {}
    
    if game_config["teams"] == 2:
        team_names = ["red", "blue"]
    elif game_config["teams"] == 3:
        team_names = ["red", "pink", "orange"]
    else:  # 4 teams
        team_names = ["red", "blue", "maple", "mud"]
    
    for i, team in enumerate(team_names):
        teams[team] = {
            "spy": None,
            "guessers": [],
            "cards": game_config["cards"][i],
            "color": TEAM_COLORS[team]["emoji"],
            "score": 0,
            "hints": []
        }
    
    return teams

async def send_game_lobby(update, context, game, mode):
    teams = game.teams
    mode_display = mode.replace('_', ' ').title()
    
    # Create team display
    team_display = ""
    for team_name, team_data in teams.items():
        team_display += f"\n{team_data['color']} *{team_name.upper()} TEAM:*"
        team_display += f"\n🕵️ Spy: {team_data['spy'] or 'None'}"
        team_display += f"\n👥 Guessers: {', '.join(team_data['guessers']) if team_data['guessers'] else 'None'}"
        team_display += f"\n🎴 Cards: {team_data['cards']}\n"
    
    lobby_text = f"""
🎮 *ADVANCED MEDCODI GAME* 🎮

*Mode:* {mode_display}
*Status:* Waiting for players...
*Turn Time:* 6 minutes

{team_display}

*Click buttons below to join!*
    """
    
    # Create advanced join buttons
    keyboard = []
    for team_name, team_data in teams.items():
        keyboard.append([
            InlineKeyboardButton(f"🕵️ {team_name.title()} Spy", callback_data=f"join_spy_{team_name}"),
            InlineKeyboardButton(f"👥 {team_name.title()} Guesser", callback_data=f"join_guesser_{team_name}")
        ])
    
    keyboard.append([
        InlineKeyboardButton("🎨 Change Color", callback_data="change_color"),
        InlineKeyboardButton("🚪 Leave", callback_data="leave_game")
    ])
    keyboard.append([
        InlineKeyboardButton("🎯 Begin Game", callback_data="begin_game"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_game")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_markdown(lobby_text, reply_markup=reply_markup)

# ADD THESE MISSING FUNCTIONS
async def advanced_end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game = db_manager.get_active_game(chat_id)
    
    if game:
        db_manager.update_game_state(game.id, 'ended')
        await update.message.reply_text("🛑 Game ended by admin!")
    else:
        await update.message.reply_text("❌ No active game found!")

async def advanced_skip_turn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game = db_manager.get_active_game(chat_id)
    
    if game and game.state == 'started':
        # Skip turn logic would go here
        await update.message.reply_text("⏩ Turn skipped!")
    else:
        await update.message.reply_text("❌ No active game or game not started!")

async def card_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /card word")
        return
    
    word = " ".join(context.args)
    # Card guess logic would go here
    await update.message.reply_text(f"🎴 Guessing card: {word}")

async def handle_advanced_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle game-related messages
    message_text = update.message.text
    chat_id = update.effective_chat.id
    
    game = db_manager.get_active_game(chat_id)
    if game and game.state == 'started':
        # Process game messages (hints, guesses, etc.)
        if message_text.isupper() and len(message_text) > 2:
            # Likely a card guess
            await update.message.reply_text(f"🎴 Processing guess: {message_text}")
        elif len(message_text.split()) >= 2:
            # Likely a hint
            await update.message.reply_text(f"💡 Processing hint: {message_text}")
