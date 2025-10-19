import logging
import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
import handlers.start_handler as start_handler
import handlers.dictionary_handler as dictionary_handler
import handlers.medcodi_handler as medcodi_handler
import handlers.quiz_handler as quiz_handler
import handlers.grammar_quiz_handler as grammar_quiz_handler
import handlers.payment_handler as payment_handler
import handlers.shop_handler as shop_handler
import handlers.settings_handler as settings_handler
import handlers.callback_handler as callback_handler

# Advanced logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='logs/bot.log',
    filemode='a'
)

class AdvancedWordMasterBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
        
    def setup_handlers(self):
        # Start and help
        self.application.add_handler(CommandHandler("start", start_handler.advanced_start))
        self.application.add_handler(CommandHandler("help", start_handler.advanced_help))
        self.application.add_handler(CommandHandler("info", start_handler.bot_info))
        
        # AI Dictionary
        self.application.add_handler(CommandHandler("ud", dictionary_handler.advanced_ud_command))
        self.application.add_handler(CommandHandler("define", dictionary_handler.advanced_ud_command))
        
        # Advanced Medcodi Game System
        medcodi_commands = [
            "medcodi_two_emoji", "medcodi_two", "medcodi_two_black",
            "medcodi_two_supercrazy", "medcodi_two_sevenball", "medcodi_two_crazy",
            "medcodi_triple_classic", "medcodi_triple_crazy", "medcodi_two_adventure",
            "medcodi_triple_black", "medcodi_triple_emoji", "medcodi_two_insane",
            "medcodi_three_insane", "medcodi_four_classic", "medcodi_four_emoji",
            "medcodi_two_emoji_black", "medcodi_triple_supercrazy", "medcodi_random"
        ]
        
        for cmd in medcodi_commands:
            self.application.add_handler(CommandHandler(cmd, medcodi_handler.create_advanced_medcodi_game))
        
        # Quiz Systems
        self.application.add_handler(CommandHandler("quiz_image", quiz_handler.start_advanced_quiz))
        self.application.add_handler(CommandHandler("grammar_quiz", grammar_quiz_handler.start_advanced_grammar_quiz))
        self.application.add_handler(CommandHandler("quick_quiz", quiz_handler.quick_quiz))
        
        # Advanced Economy System
        self.application.add_handler(CommandHandler("daily", payment_handler.advanced_daily_bonus))
        self.application.add_handler(CommandHandler("pay", payment_handler.advanced_pay_coins))
        self.application.add_handler(CommandHandler("transfer", payment_handler.transfer_coins))
        self.application.add_handler(CommandHandler("donate", payment_handler.donate_coins))
        
        # Advanced Shop System
        self.application.add_handler(CommandHandler("shop", shop_handler.advanced_shop))
        self.application.add_handler(CommandHandler("buy", shop_handler.advanced_buy))
        self.application.add_handler(CommandHandler("sell", shop_handler.advanced_sell))
        self.application.add_handler(CommandHandler("gift", shop_handler.advanced_gift))
        self.application.add_handler(CommandHandler("inventory", shop_handler.show_inventory))
        self.application.add_handler(CommandHandler("market", shop_handler.show_market))
        
        # Advanced Settings
        self.application.add_handler(CommandHandler("settings", settings_handler.advanced_settings))
        self.application.add_handler(CommandHandler("time", settings_handler.set_advanced_time))
        self.application.add_handler(CommandHandler("wordpack", settings_handler.advanced_wordpack))
        self.application.add_handler(CommandHandler("language", settings_handler.change_language))
        
        # Game Management
        self.application.add_handler(CommandHandler("medcodi_end", medcodi_handler.advanced_end_game))
        self.application.add_handler(CommandHandler("skip", medcodi_handler.advanced_skip_turn))
        self.application.add_handler(CommandHandler("card", medcodi_handler.card_guess))
        
        # Stats and Leaderboards
        self.application.add_handler(CommandHandler("stats", payment_handler.advanced_stats))
        self.application.add_handler(CommandHandler("leaderboard", payment_handler.advanced_leaderboard))
        self.application.add_handler(CommandHandler("profile", payment_handler.user_profile))
        self.application.add_handler(CommandHandler("top", payment_handler.top_players))
        
        # Callback queries for all buttons
        self.application.add_handler(CallbackQueryHandler(callback_handler.advanced_callback_handler))
        
        # Message handlers for game inputs
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, medcodi_handler.handle_advanced_message))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def error_handler(self, update, context):
        logging.error(f"Exception while handling an update: {context.error}")
    
    def run(self):
        print("🤖 Advanced Word Master Bot Started Successfully!")
        print("🎮 All Game Modes: Active")
        print("💰 Economy System: Active") 
        print("🛍️ Shop System: Active")
        print("📚 AI Dictionary: Active")
        print("⏰ Timer System: Active")
        self.application.run_polling()

if __name__ == "__main__":
    bot = AdvancedWordMasterBot()
    bot.run()
