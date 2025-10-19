import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_manager import db_manager
from config import GRAMMAR_COINS

# Advanced grammar questions database
GRAMMAR_QUESTIONS = [
    {
        'question': 'Choose the correct sentence:',
        'options': [
            'She don\'t like apples.',
            'She doesn\'t like apples.',
            'She doesn\'t likes apples.',
            'She don\'t likes apples.'
        ],
        'correct': 1,
        'explanation': 'Use \"doesn\'t\" with third person singular (she/he/it).',
        'difficulty': 'easy',
        'category': 'verbs'
    },
    {
        'question': 'Which sentence is in the present perfect tense?',
        'options': [
            'I am going to the store.',
            'I went to the store.',
            'I have gone to the store.',
            'I go to the store.'
        ],
        'correct': 2,
        'explanation': 'Present perfect: have/has + past participle.',
        'difficulty': 'medium',
        'category': 'tenses'
    },
    {
        'question': 'Identify the conditional sentence:',
        'options': [
            'If it rains, we will cancel the picnic.',
            'It is raining outside.',
            'We cancelled the picnic yesterday.',
            'It might rain later.'
        ],
        'correct': 0,
        'explanation': 'Conditional sentences use \"if\" + present simple, will + infinitive.',
        'difficulty': 'medium',
        'category': 'conditionals'
    },
    {
        'question': 'Choose the correct relative pronoun:',
        'options': [
            'The man which is standing there is my uncle.',
            'The man who is standing there is my uncle.',
            'The man whom is standing there is my uncle.',
            'The man whose is standing there is my uncle.'
        ],
        'correct': 1,
        'explanation': 'Use \"who\" for people as subjects.',
        'difficulty': 'medium',
        'category': 'pronouns'
    },
    {
        'question': 'Which sentence uses the passive voice correctly?',
        'options': [
            'The cake was eaten by the children.',
            'The children eaten the cake.',
            'The cake is eating by the children.',
            'The children was eaten the cake.'
        ],
        'correct': 0,
        'explanation': 'Passive voice: object + be + past participle + by + subject.',
        'difficulty': 'hard',
        'category': 'voice'
    },
    {
        'question': 'Identify the sentence with correct article usage:',
        'options': [
            'She is a honest person.',
            'She is an honest person.',
            'She is the honest person.',
            'She is honest person.'
        ],
        'correct': 1,
        'explanation': 'Use \"an\" before words starting with a vowel sound.',
        'difficulty': 'easy',
        'category': 'articles'
    },
    {
        'question': 'Choose the correct preposition:',
        'options': [
            'She is good in mathematics.',
            'She is good at mathematics.',
            'She is good with mathematics.',
            'She is good on mathematics.'
        ],
        'correct': 1,
        'explanation': 'The correct preposition with \"good\" is \"at\" for skills.',
        'difficulty': 'medium',
        'category': 'prepositions'
    },
    {
        'question': 'Which sentence is grammatically correct?',
        'options': [
            'Neither of the students have completed their homework.',
            'Neither of the students has completed their homework.',
            'Neither of the students have completed his homework.',
            'Neither of the students has completed his homework.'
        ],
        'correct': 1,
        'explanation': '\"Neither\" is singular, so use \"has\" and \"their\" for gender neutrality.',
        'difficulty': 'hard',
        'category': 'agreement'
    },
    {
        'question': 'Select the properly punctuated sentence:',
        'options': [
            'I like apples, oranges and bananas.',
            'I like apples, oranges, and bananas.',
            'I like apples oranges and bananas.',
            'I like apples oranges, and bananas.'
        ],
        'correct': 1,
        'explanation': 'Use Oxford comma before \"and\" in a list for clarity.',
        'difficulty': 'medium',
        'category': 'punctuation'
    },
    {
        'question': 'Identify the sentence fragment:',
        'options': [
            'Running quickly through the park.',
            'He was running quickly through the park.',
            'While he was running through the park.',
            'The man running through the park.'
        ],
        'correct': 0,
        'explanation': 'A sentence fragment lacks a subject and/or verb.',
        'difficulty': 'hard',
        'category': 'sentence_structure'
    }
]

class AdvancedGrammarQuiz:
    def __init__(self, chat_id, difficulty=None, category=None):
        self.chat_id = chat_id
        self.difficulty = difficulty
        self.category = category
        self.current_question = None
        self.score = 0
        self.questions_answered = 0
        self.max_questions = 5
        self.used_questions = set()
    
    async def start_advanced_grammar_quiz(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_question(update, context)
    
    async def send_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Filter questions by difficulty and category
        filtered_questions = GRAMMAR_QUESTIONS
        
        if self.difficulty:
            filtered_questions = [q for q in filtered_questions if q['difficulty'] == self.difficulty]
        
        if self.category:
            filtered_questions = [q for q in filtered_questions if q['category'] == self.category]
        
        # Remove already used questions
        available_questions = [q for i, q in enumerate(filtered_questions) if i not in self.used_questions]
        
        if not available_questions:
            # Reset used questions if all have been used
            self.used_questions = set()
            available_questions = filtered_questions
        
        if not available_questions:
            await update.message.reply_text("❌ No questions available with selected filters!")
            return
        
        self.current_question = random.choice(available_questions)
        self.used_questions.add(GRAMMAR_QUESTIONS.index(self.current_question))
        self.questions_answered += 1
        
        quiz_text = f"""
📝 *ADVANCED GRAMMAR QUIZ*

🏷️ *Category:* {self.current_question['category'].title()}
⭐ *Difficulty:* {self.current_question['difficulty'].title()}
💰 *Reward per question:* {GRAMMAR_COINS} coins
📊 *Progress:* {self.questions_answered}/{self.max_questions}
🎯 *Score:* {self.score}

*Question {self.questions_answered}:* {self.current_question['question']}
        """
        
        # Create options keyboard
        keyboard = []
        options = self.current_question['options']
        for i, option in enumerate(options):
            keyboard.append([InlineKeyboardButton(
                f"{chr(65+i)}. {option}",
                callback_data=f"grammar_answer_{i}"
            )])
        
        if self.questions_answered > 1:
            keyboard.append([InlineKeyboardButton("⏹️ End Quiz", callback_data="grammar_end")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            quiz_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def process_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE, answer_index: int, user):
        query = update.callback_query
        await query.answer()
        
        is_correct = (answer_index == self.current_question['correct'])
        correct_answer = self.current_question['options'][self.current_question['correct']]
        
        if is_correct:
            self.score += 1
            result_text = f"✅ *CORRECT!* {user.first_name}\n\n"
            
            # Reward player
            user_data = db_manager.get_user(user.id)
            if user_data:
                db_manager.update_user_coins(user.id, GRAMMAR_COINS)
            
            result_text += f"💰 *Reward:* {GRAMMAR_COINS} coins\n"
        else:
            result_text = f"❌ *INCORRECT!* {user.first_name}\n\n"
            result_text += f"✅ *Correct Answer:* {correct_answer}\n"
        
        result_text += f"💡 *Explanation:* {self.current_question['explanation']}\n"
        result_text += f"🎯 *Current Score:* {self.score}/{self.questions_answered}"
        
        # Check if quiz should continue
        if self.questions_answered < self.max_questions:
            keyboard = [
                [InlineKeyboardButton("➡️ Next Question", callback_data="grammar_next")],
                [InlineKeyboardButton("⏹️ End Quiz", callback_data="grammar_end")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("🏆 Show Results", callback_data="grammar_results")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            result_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        total_coins = self.score * GRAMMAR_COINS
        accuracy = (self.score / self.questions_answered) * 100
        
        results_text = f"""
🏆 *GRAMMAR QUIZ RESULTS*

📊 *Final Score:* {self.score}/{self.questions_answered}
🎯 *Accuracy:* {accuracy:.1f}%
💰 *Total Coins Earned:* {total_coins} coins

⭐ *Performance Rating:*
{'🏅 Grammar Master' if accuracy >= 90 else '🎯 Grammar Pro' if accuracy >= 70 else '📚 Learning Well' if accuracy >= 50 else '💪 Keep Practicing'}
        """
        
        # Update user stats
        user = update.callback_query.from_user
        user_data = db_manager.get_user(user.id)
        if user_data:
            user_data.total_coins_earned += total_coins
        
        keyboard = [
            [InlineKeyboardButton("🔄 Play Again", callback_data="grammar_restart"),
             InlineKeyboardButton("🎯 New Difficulty", callback_data="grammar_difficulty")],
            [InlineKeyboardButton("📊 My Stats", callback_data="user_stats"),
             InlineKeyboardButton("🎮 Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query = update.callback_query
        await query.edit_message_text(
            results_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def start_advanced_grammar_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    difficulty = None
    category = None
    
    if context.args:
        for arg in context.args:
            if arg in ['easy', 'medium', 'hard']:
                difficulty = arg
            else:
                # Assume it's a category
                category = arg
    
    grammar_quiz = AdvancedGrammarQuiz(update.effective_chat.id, difficulty, category)
    context.chat_data['current_grammar_quiz'] = grammar_quiz
    await grammar_quiz.start_advanced_grammar_quiz(update, context)

async def handle_grammar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    query = update.callback_query
    user = query.from_user
    
    if data.startswith('grammar_answer_'):
        answer_index = int(data.replace('grammar_answer_', ''))
        grammar_quiz = context.chat_data.get('current_grammar_quiz')
        if grammar_quiz:
            await grammar_quiz.process_answer(update, context, answer_index, user)
    
    elif data == 'grammar_next':
        grammar_quiz = context.chat_data.get('current_grammar_quiz')
        if grammar_quiz:
            await grammar_quiz.send_question(update, context)
    
    elif data == 'grammar_results':
        grammar_quiz = context.chat_data.get('current_grammar_quiz')
        if grammar_quiz:
            await grammar_quiz.show_results(update, context)
    
    elif data == 'grammar_restart':
        grammar_quiz = context.chat_data.get('current_grammar_quiz')
        if grammar_quiz:
            # Reset quiz with same settings
            new_quiz = AdvancedGrammarQuiz(update.effective_chat.id, 
                                         grammar_quiz.difficulty, 
                                         grammar_quiz.category)
            context.chat_data['current_grammar_quiz'] = new_quiz
            await new_quiz.start_advanced_grammar_quiz(update, context)
    
    elif data == 'grammar_difficulty':
        # Show difficulty selection
        keyboard = [
            [InlineKeyboardButton("😊 Easy", callback_data="grammar_diff_easy"),
             InlineKeyboardButton("😐 Medium", callback_data="grammar_diff_medium")],
            [InlineKeyboardButton("😰 Hard", callback_data="grammar_diff_hard"),
             InlineKeyboardButton("🎲 Random", callback_data="grammar_diff_random")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📚 *Select Difficulty Level:*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data.startswith('grammar_diff_'):
        difficulty = data.replace('grammar_diff_', '')
        if difficulty == 'random':
            difficulty = None
        
        grammar_quiz = AdvancedGrammarQuiz(update.effective_chat.id, difficulty)
        context.chat_data['current_grammar_quiz'] = grammar_quiz
        await grammar_quiz.start_advanced_grammar_quiz(update, context)
    
    elif data == 'grammar_end':
        grammar_quiz = context.chat_data.get('current_grammar_quiz')
        if grammar_quiz:
            await grammar_quiz.show_results(update, context)
            context.chat_data['current_grammar_quiz'] = None

# Add callback handler integration
async def grammar_quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data.startswith('grammar_'):
        await handle_grammar_callback(update, context, data)
