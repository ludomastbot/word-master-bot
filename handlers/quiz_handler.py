import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_manager import db_manager
from config import QUIZ_COINS
from utils.image_generator import generate_quiz_image

# Advanced quiz questions database
QUIZ_DATABASE = {
    'animals': [
        {
            'question': 'What animal is this?',
            'image_url': 'https://example.com/tiger.jpg',  # In real implementation, use actual URLs
            'options': ['Tiger', 'Lion', 'Leopard', 'Cheetah'],
            'correct': 0,
            'difficulty': 'medium'
        },
        {
            'question': 'Identify this marine animal',
            'image_url': 'https://example.com/dolphin.jpg',
            'options': ['Dolphin', 'Shark', 'Whale', 'Seal'],
            'correct': 0,
            'difficulty': 'easy'
        }
    ],
    'landmarks': [
        {
            'question': 'Which famous landmark is this?',
            'image_url': 'https://example.com/eiffel.jpg',
            'options': ['Eiffel Tower', 'Big Ben', 'Statue of Liberty', 'Colosseum'],
            'correct': 0,
            'difficulty': 'easy'
        },
        {
            'question': 'Where is this ancient wonder located?',
            'image_url': 'https://example.com/pyramid.jpg',
            'options': ['Egypt', 'Mexico', 'Peru', 'China'],
            'correct': 0,
            'difficulty': 'medium'
        }
    ],
    'flags': [
        {
            'question': 'Which country does this flag belong to?',
            'image_url': 'https://example.com/usa_flag.jpg',
            'options': ['United States', 'United Kingdom', 'France', 'Germany'],
            'correct': 0,
            'difficulty': 'easy'
        }
    ],
    'movies': [
        {
            'question': 'From which movie is this scene?',
            'image_url': 'https://example.com/movie_scene.jpg',
            'options': ['Avatar', 'Titanic', 'Avengers', 'Jurassic Park'],
            'correct': 0,
            'difficulty': 'hard'
        }
    ]
}

class AdvancedQuizGame:
    def __init__(self, chat_id, category=None):
        self.chat_id = chat_id
        self.category = category or random.choice(list(QUIZ_DATABASE.keys()))
        self.current_question = None
        self.players_answered = {}
        self.correct_answers = 0
        self.question_start_time = None
        self.timer_task = None
    
    async def start_advanced_quiz(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_question(update, context)
    
    async def send_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Get random question from category
        questions = QUIZ_DATABASE.get(self.category, [])
        if not questions:
            await update.message.reply_text("❌ No questions available in this category!")
            return
        
        self.current_question = random.choice(questions)
        self.players_answered = {}
        self.question_start_time = asyncio.get_event_loop().time()
        
        # Generate quiz image
        image = generate_quiz_image(
            self.current_question['question'],
            self.current_question['options'],
            self.current_question['correct']
        )
        
        # Create options keyboard
        keyboard = []
        options = self.current_question['options']
        for i, option in enumerate(options):
            keyboard.append([InlineKeyboardButton(
                f"{chr(65+i)}. {option}",
                callback_data=f"quiz_answer_{i}"
            )])
        
        keyboard.append([InlineKeyboardButton("⏹️ End Quiz", callback_data="quiz_end")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        quiz_text = f"""
📚 *ADVANCED IMAGE QUIZ*

🏷️ *Category:* {self.category.title()}
⭐ *Difficulty:* {self.current_question['difficulty'].title()}
💰 *Reward:* {QUIZ_COINS} coins
⏰ *Time Limit:* 30 seconds

*Question:* {self.current_question['question']}
        """
        
        # Send quiz (in real implementation, you'd send actual image)
        # For now, we'll send text with generated image
        await update.message.reply_photo(
            photo=image,
            caption=quiz_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Start timer
        self.timer_task = asyncio.create_task(self.quiz_timer(update, context))
    
    async def quiz_timer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await asyncio.sleep(30)  # 30 second timer
            
            # Time's up - show results
            await self.show_results(update, context, timed_out=True)
            
        except asyncio.CancelledError:
            pass
    
    async def process_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE, answer_index: int, user):
        query = update.callback_query
        await query.answer()
        
        if user.id in self.players_answered:
            await query.answer("❌ You already answered this question!", show_alert=True)
            return
        
        self.players_answered[user.id] = answer_index
        
        is_correct = (answer_index == self.current_question['correct'])
        
        if is_correct:
            # Calculate time bonus
            time_taken = asyncio.get_event_loop().time() - self.question_start_time
            time_bonus = max(0, int((30 - time_taken) * 2))  # Up to 60 bonus coins
            
            total_coins = QUIZ_COINS + time_bonus
            self.correct_answers += 1
            
            # Reward player
            user_data = db_manager.get_user(user.id)
            if user_data:
                db_manager.update_user_coins(user.id, total_coins)
            
            await query.edit_message_caption(
                caption=f"✅ *CORRECT!* {user.first_name}\n\n"
                       f"💰 *Reward:* {total_coins} coins ({QUIZ_COINS} + {time_bonus} time bonus)\n"
                       f"⏱️ *Time:* {time_taken:.1f}s\n"
                       f"🎯 *Correct Answers:* {self.correct_answers}",
                parse_mode='Markdown'
            )
        else:
            correct_answer = self.current_question['options'][self.current_question['correct']]
            await query.edit_message_caption(
                caption=f"❌ *WRONG!* {user.first_name}\n\n"
                       f"✅ *Correct Answer:* {correct_answer}\n"
                       f"🎯 *Correct Answers:* {self.correct_answers}",
                parse_mode='Markdown'
            )
        
        # Cancel timer
        if self.timer_task:
            self.timer_task.cancel()
        
        # Wait a bit then send next question
        await asyncio.sleep(3)
        await self.send_question(update, context)
    
    async def show_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE, timed_out=False):
        if timed_out:
            results_text = "⏰ *TIME'S UP!*\n\n"
        else:
            results_text = "🎯 *QUIZ RESULTS*\n\n"
        
        results_text += f"✅ *Correct Answers:* {self.correct_answers}\n"
        results_text += f"👥 *Players Participated:* {len(self.players_answered)}\n"
        
        if self.correct_answers > 0:
            results_text += f"💰 *Total Coins Earned:* {self.correct_answers * QUIZ_COINS}\n"
        
        results_text += f"\n🏷️ *Category:* {self.category.title()}"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Play Again", callback_data="quiz_restart"),
             InlineKeyboardButton("🎯 New Category", callback_data="quiz_new_category")],
            [InlineKeyboardButton("🎮 Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if timed_out:
            await context.bot.send_message(
                chat_id=self.chat_id,
                text=results_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            query = update.callback_query
            await query.edit_message_caption(
                caption=results_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

async def start_advanced_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = None
    if context.args:
        category = context.args[0].lower()
        if category not in QUIZ_DATABASE:
            await update.message.reply_text(
                f"❌ Category '{category}' not found!\n\n"
                f"*Available Categories:*\n"
                f"• animals\n• landmarks\n• flags\n• movies",
                parse_mode='Markdown'
            )
            return
    
    quiz_game = AdvancedQuizGame(update.effective_chat.id, category)
    context.chat_data['current_quiz'] = quiz_game
    await quiz_game.start_advanced_quiz(update, context)

async def quick_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Start a quick 5-question quiz
    quiz_game = AdvancedQuizGame(update.effective_chat.id)
    context.chat_data['current_quiz'] = quiz_game
    await quiz_game.start_advanced_quiz(update, context)

async def handle_quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    query = update.callback_query
    user = query.from_user
    
    if data.startswith('quiz_answer_'):
        answer_index = int(data.replace('quiz_answer_', ''))
        quiz_game = context.chat_data.get('current_quiz')
        if quiz_game:
            await quiz_game.process_answer(update, context, answer_index, user)
    
    elif data == 'quiz_restart':
        quiz_game = context.chat_data.get('current_quiz')
        if quiz_game:
            await quiz_game.send_question(update, context)
    
    elif data == 'quiz_new_category':
        # Show category selection
        keyboard = []
        for category in QUIZ_DATABASE.keys():
            keyboard.append([InlineKeyboardButton(
                category.title(),
                callback_data=f"quiz_category_{category}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_caption(
            caption="🎯 *Select Quiz Category:*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data.startswith('quiz_category_'):
        category = data.replace('quiz_category_', '')
        quiz_game = AdvancedQuizGame(update.effective_chat.id, category)
        context.chat_data['current_quiz'] = quiz_game
        await quiz_game.start_advanced_quiz(update, context)
    
    elif data == 'quiz_end':
        quiz_game = context.chat_data.get('current_quiz')
        if quiz_game:
            await quiz_game.show_results(update, context)
            context.chat_data['current_quiz'] = None
