import aiohttp
import json
from telegram import Update
from telegram.ext import ContextTypes
from config import AI_DICTIONARY_APIS

async def advanced_ud_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("📚 Usage: `/ud word` or `/define word`\nExample: `/ud artificial intelligence`", parse_mode='Markdown')
        return
    
    word = " ".join(context.args)
    await update.message.reply_chat_action('typing')
    
    try:
        # Multiple API calls for comprehensive results
        results = await fetch_ai_definitions(word)
        
        if results:
            response = format_advanced_definition(word, results)
        else:
            response = f"❌ No definition found for *{word}*\n\nTry:\n• Checking spelling\n• Using different words\n• Being more specific"
        
        # Split long messages
        if len(response) > 4000:
            parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for part in parts:
                await update.message.reply_markdown(part)
        else:
            await update.message.reply_markdown(response)
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error fetching definition: {str(e)}")

async def fetch_ai_definitions(word: str):
    results = {}
    
    async with aiohttp.ClientSession() as session:
        # Urban Dictionary
        try:
            async with session.get(AI_DICTIONARY_APIS["urban"].format(word), timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('list'):
                        results['urban'] = data['list'][0]
        except:
            pass
        
        # Wikipedia
        try:
            async with session.get(AI_DICTIONARY_APIS["wiki"].format(word), timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    results['wikipedia'] = data
        except:
            pass
        
        # Google Dictionary
        try:
            async with session.get(AI_DICTIONARY_APIS["google"].format(word), timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    results['dictionary'] = data
        except:
            pass
    
    return results

def format_advanced_definition(word: str, results: dict):
    response = f"📖 *Definition for: {word.upper()}*\n\n"
    
    # Dictionary definition
    if 'dictionary' in results:
        data = results['dictionary'][0] if isinstance(results['dictionary'], list) else results['dictionary']
        
        if 'meanings' in data:
            for meaning in data['meanings'][:2]:  # First 2 meanings
                part_of_speech = meaning.get('partOfSpeech', '')
                definitions = meaning.get('definitions', [])
                
                response += f"*{part_of_speech.upper()}*\n"
                for i, definition in enumerate(definitions[:3]):  # First 3 definitions
                    response += f"• {definition['definition']}\n"
                    if 'example' in definition:
                        response += f"  _Example: {definition['example']}_\n"
                response += "\n"
    
    # Wikipedia summary
    if 'wikipedia' in results:
        wiki = results['wikipedia']
        if 'extract' in wiki:
            response += f"*🌐 Wikipedia Summary:*\n{wiki['extract'][:300]}...\n\n"
    
    # Urban Dictionary
    if 'urban' in results:
        urban = results['urban']
        response += f"*💬 Urban Dictionary:*\n{urban['definition'][:300]}...\n\n"
        if 'example' in urban:
            response += f"*Example:* {urban['example'][:200]}...\n"
    
    # Additional info
    response += "\n*🔍 Sources:* Dictionary API, Wikipedia, Urban Dictionary"
    
    return response
