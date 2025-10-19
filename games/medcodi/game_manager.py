import random
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_manager import db_manager
from config import TEAM_COLORS, GAME_MODES
from utils.image_generator import generate_advanced_board_image

class AdvancedMedcodiGame:
    def __init__(self, game_data):
        self.game_data = game_data
        self.game_id = game_data.id
        self.chat_id = game_data.chat_id
        self.mode = game_data.mode
        self.teams = game_data.teams
        self.board = []
        self.current_turn = None
        self.hint = None
        self.revealed_cards = []
        self.turn_start_time = None
        self.timer_task = None
        
    async def start_game(self, query, context):
        # Generate game board
        self.generate_advanced_board()
        
        # Set first turn randomly
        self.current_turn = random.choice(list(self.teams.keys()))
        self.turn_start_time = datetime.utcnow()
        
        # Update game state
        db_manager.update_game_state(self.game_id, 'started', {
            'board': self.board,
            'current_turn': self.current_turn,
            'started_at': datetime.utcnow()
        })
        
        # Send initial game board
        await self.send_game_board(query, context)
        
        # Start timer
        self.timer_task = asyncio.create_task(self.game_timer(context))
    
    def generate_advanced_board(self):
        words = self.get_advanced_word_list()
        game_config = GAME_MODES[self.mode]
        team_names = list(self.teams.keys())
        
        # Initialize card distribution
        cards_needed = sum(game_config['cards'])
        selected_words = random.sample(words, cards_needed)
        
        self.board = []
        card_index = 0
        
        # Assign cards to teams
        for i, team_name in enumerate(team_names):
            team_cards_count = game_config['cards'][i]
            for _ in range(team_cards_count):
                self.board.append({
                    'word': selected_words[card_index],
                    'color': team_name,
                    'revealed': False,
                    'index': card_index
                })
                card_index += 1
        
        # Add white/black cards based on mode
        if 'black' in self.mode:
            self.board.append({
                'word': selected_words[card_index],
                'color': 'black',
                'revealed': False,
                'index': card_index
            })
            card_index += 1
        
        # Add white cards
        white_cards_count = game_config['cards'][-1] if game_config['cards'][-1] < 10 else 1
        for _ in range(white_cards_count):
            self.board.append({
                'word': selected_words[card_index],
                'color': 'white',
                'revealed': False,
                'index': card_index
            })
            card_index += 1
        
        # Shuffle board
        random.shuffle(self.board)
    
    def get_advanced_word_list(self):
        # Advanced word list with categories
        categories = {
            'animals': ['tiger', 'elephant', 'giraffe', 'penguin', 'dolphin', 'kangaroo'],
            'countries': ['japan', 'brazil', 'canada', 'egypt', 'australia', 'india'],
            'professions': ['doctor', 'engineer', 'teacher', 'artist', 'chef', 'scientist'],
            'technology': ['computer', 'smartphone', 'internet', 'robot', 'software', 'hardware'],
            'food': ['pizza', 'sushi', 'pasta', 'burger', 'salad', 'dessert'],
            'sports': ['football', 'basketball', 'tennis', 'cricket', 'swimming', 'cycling'],
            'movies': ['avatar', 'titanic', 'inception', 'matrix', 'jurassic', 'avengers'],
            'science': ['physics', 'chemistry', 'biology', 'astronomy', 'geology', 'mathematics']
        }
        
        # Combine all words
        all_words = []
        for category_words in categories.values():
            all_words.extend(category_words)
        
        return all_words
    
    async def send_game_board(self, query, context, hint_text=None):
        # Generate and send game board image
        image = generate_advanced_board_image(self.board, self.teams, self.mode, self.current_turn)
        
        caption = self.get_board_caption(hint_text)
        
        # Create action buttons
        keyboard = [
            [InlineKeyboardButton("⏩ Skip Turn", callback_data="skip_turn"),
             InlineKeyboardButton("🛑 End Game", callback_data="end_game")],
            [InlineKeyboardButton("📊 Game Stats", callback_data="game_stats"),
             InlineKeyboardButton("❓ Help", callback_data="game_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if hasattr(query, 'edit_message_media'):
            await query.edit_message_media(
                media=image,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_photo(
                chat_id=self.chat_id,
                photo=image,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    def get_board_caption(self, hint_text=None):
        caption = f"🎮 *MEDCODI GAME - {self.mode.upper().replace('_', ' ')}*\n\n"
        
        # Team status
        for team_name, team_data in self.teams.items():
            remaining_cards = len([card for card in self.board if card['color'] == team_name and not card['revealed']])
            caption += f"{team_data['color']} *{team_name.upper()}*: {remaining_cards}/{team_data['cards']} cards\n"
        
        caption += f"\n🎯 *Current Turn:* {self.current_turn.upper()} Team\n"
        
        if hint_text:
            caption += f"\n💡 *Hint:* {hint_text}\n"
        
        if self.teams[self.current_turn]['spy']:
            caption += f"🕵️ *Spy:* {self.teams[self.current_turn]['spy']}\n"
        
        guessers = self.teams[self.current_turn]['guessers']
        if guessers:
            caption += f"👥 *Guessers:* {', '.join(guessers)}\n"
        
        caption += f"\n⏰ *Time Left:* 6:00 minutes"
        
        return caption
    
    async def game_timer(self, context):
        try:
            total_time = 360  # 6 minutes
            while total_time > 0:
                await asyncio.sleep(60)  # Update every minute
                total_time -= 60
                
                # Send time update
                minutes = total_time // 60
                seconds = total_time % 60
                
                if minutes <= 1:  # Last minute warning
                    await context.bot.send_message(
                        chat_id=self.chat_id,
                        text=f"⏰ *TIME WARNING:* {minutes}:{seconds:02d} left for {self.current_turn} team!",
                        parse_mode='Markdown'
                    )
            
            # Time's up - skip turn
            await self.skip_turn_auto(context)
            
        except asyncio.CancelledError:
            pass
    
    async def skip_turn_auto(self, context):
        await context.bot.send_message(
            chat_id=self.chat_id,
            text=f"⏰ Time's up! {self.current_turn.title()} team's turn skipped."
        )
        await self.next_turn(context)
    
    async def next_turn(self, context):
        team_names = list(self.teams.keys())
        current_index = team_names.index(self.current_turn)
        next_index = (current_index + 1) % len(team_names)
        self.current_turn = team_names[next_index]
        
        # Update game data
        db_manager.update_game_turn(self.game_id, self.current_turn)
        
        # Reset hint
        self.hint = None
        
        # Send new turn notification
        await context.bot.send_message(
            chat_id=self.chat_id,
            text=f"🔄 *TURN CHANGE:* Now it's {self.current_turn.title()} team's turn!",
            parse_mode='Markdown'
        )
        
        # Send updated board
        await self.send_game_board(None, context)
    
    async def process_hint(self, hint_text, spy_name, context):
        if self.teams[self.current_turn]['spy'] != spy_name:
            await context.bot.send_message(
                chat_id=self.chat_id,
                text="❌ Only the current team's spy can give hints!"
            )
            return False
        
        # Validate hint based on game mode
        if not self.validate_hint(hint_text):
            await context.bot.send_message(
                chat_id=self.chat_id,
                text="❌ Invalid hint format! Check game rules."
            )
            return False
        
        self.hint = {
            'text': hint_text,
            'given_by': spy_name,
            'timestamp': datetime.utcnow()
        }
        
        # Store hint in team data
        self.teams[self.current_turn]['hints'].append(self.hint)
        
        await context.bot.send_message(
            chat_id=self.chat_id,
            text=f"💡 *HINT RECEIVED from {spy_name}:* {hint_text}",
            parse_mode='Markdown'
        )
        
        # Update board with hint
        await self.send_game_board(None, context, hint_text)
        return True
    
    def validate_hint(self, hint_text):
        if 'emoji' in self.mode:
            # Emoji mode validation
            parts = hint_text.strip().split()
            if len(parts) != 2:
                return False
            emoji, number = parts
            # Check if first part is emoji and second is single digit
            return len(number) == 1 and number.isdigit()
        else:
            # Word mode validation
            parts = hint_text.strip().split()
            if len(parts) < 2:
                return False
            number = parts[-1]
            # Check if last part is a number
            return number.isdigit() and 0 <= int(number) <= 9
    
    async def process_guess(self, word, guesser_name, context):
        # Find the card
        card_index = None
        for i, card in enumerate(self.board):
            if card['word'].lower() == word.lower() and not card['revealed']:
                card_index = i
                break
        
        if card_index is None:
            await context.bot.send_message(
                chat_id=self.chat_id,
                text=f"❌ '{word}' is not a valid card or already revealed!"
            )
            return
        
        # Reveal the card
        self.board[card_index]['revealed'] = True
        self.revealed_cards.append(card_index)
        
        card_color = self.board[card_index]['color']
        card_word = self.board[card_index]['word']
        
        # Check result
        if card_color == self.current_turn:
            # Correct guess
            await context.bot.send_message(
                chat_id=self.chat_id,
                text=f"✅ *CORRECT!* {guesser_name} revealed {self.teams[self.current_turn]['color']} {card_word}",
                parse_mode='Markdown'
            )
            
            # Check win condition
            if self.check_win_condition():
                await self.end_game(context, self.current_turn)
                return
            
            # Continue turn if hint allows more guesses
            if self.hint and self.has_more_guesses():
                await self.send_game_board(None, context, self.hint['text'])
            else:
                await self.next_turn(context)
                
        elif card_color == 'black':
            # Black card - instant loss
            await context.bot.send_message(
                chat_id=self.chat_id,
                text=f"💀 *BLACK CARD!* {guesser_name} revealed the assassin! {self.current_turn.title()} team loses!",
                parse_mode='Markdown'
            )
            await self.end_game(context, 'assassin')
            
        elif card_color == 'white':
            # White card - neutral
            await context.bot.send_message(
                chat_id=self.chat_id,
                text=f"⚪ *NEUTRAL CARD* revealed by {guesser_name}. Turn continues."
            )
            await self.send_game_board(None, context, self.hint['text'] if self.hint else None)
            
        else:
            # Wrong team's card
            await context.bot.send_message(
                chat_id=self.chat_id,
                text=f"❌ *WRONG TEAM!* {guesser_name} revealed {self.teams[card_color]['color']} {card_word}. Turn ended!",
                parse_mode='Markdown'
            )
            await self.next_turn(context)
    
    def has_more_guesses(self):
        if not self.hint:
            return False
        
        hint_parts = self.hint['text'].strip().split()
        allowed_guesses = int(hint_parts[-1]) if hint_parts[-1].isdigit() else 0
        
        # Count how many correct guesses this turn
        current_turn_cards = [card for card in self.board 
                            if card['revealed'] and card['color'] == self.current_turn]
        
        return len(current_turn_cards) < allowed_guesses + 1  # +1 for extra guess
    
    def check_win_condition(self):
        current_team_cards = [card for card in self.board if card['color'] == self.current_turn]
        revealed_team_cards = [card for card in current_team_cards if card['revealed']]
        
        return len(revealed_team_cards) == len(current_team_cards)
    
    async def end_game(self, context, winner):
        # Cancel timer
        if self.timer_task:
            self.timer_task.cancel()
        
        # Update game state
        db_manager.update_game_state(self.game_id, 'ended', {
            'winner': winner,
            'ended_at': datetime.utcnow()
        })
        
        # Distribute coins
        await self.distribute_rewards(context, winner)
        
        # Send game over message
        if winner == 'assassin':
            message = "💀 *GAME OVER - ASSASSIN REVEALED!*\n\nNo winners this round!"
        else:
            message = f"🏆 *GAME OVER - {winner.upper()} TEAM WINS!*\n\nCongratulations to {self.teams[winner]['color']} {winner.title()} team!"
        
        # Show final board
        final_image = generate_advanced_board_image(self.board, self.teams, self.mode, None, True)
        
        keyboard = [
            [InlineKeyboardButton("🔄 Play Again", callback_data="play_again"),
             InlineKeyboardButton("📊 Stats", callback_data="game_stats")],
            [InlineKeyboardButton("🎮 New Game", callback_data="new_game")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_photo(
            chat_id=self.chat_id,
            photo=final_image,
            caption=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def distribute_rewards(self, context, winner):
        from config import WIN_COINS, LOSE_COINS
        
        for team_name, team_data in self.teams.items():
            coins = WIN_COINS if team_name == winner else LOSE_COINS
            
            # Update spy coins
            if team_data['spy']:
                # In real implementation, get user_id from username
                pass
            
            # Update guessers coins
            for guesser in team_data['guessers']:
                # In real implementation, get user_id from username
                pass
            
            await context.bot.send_message(
                chat_id=self.chat_id,
                text=f"💰 {team_name.title()} team received {coins} coins!",
                parse_mode='Markdown'
            )
