import aiohttp
import json

async def get_ai_definition(word: str):
    """AI-powered dictionary function"""
    try:
        # Using multiple dictionary APIs
        async with aiohttp.ClientSession() as session:
            # Try dictionary API first
            async with session.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}") as response:
                if response.status == 200:
                    data = await response.json()
                    return format_dictionary_response(data, word)
            
            # Fallback to Urban Dictionary
            async with session.get(f"https://api.urbandictionary.com/v0/define?term={word}") as response:
                if response.status == 200:
                    data = await response.json()
                    return format_urban_response(data, word)
        
        return f"❌ No definition found for '{word}'"
    
    except Exception as e:
        return f"❌ Error fetching definition: {str(e)}"

def format_dictionary_response(data, word):
    if not data:
        return f"❌ No definition found for '{word}'"
    
    result = f"📖 *Definition for: {word.upper()}*\n\n"
    
    for entry in data[:2]:  # Show first 2 entries
        if 'meanings' in entry:
            for meaning in entry['meanings'][:2]:  # First 2 meanings
                part_of_speech = meaning.get('partOfSpeech', '')
                definitions = meaning.get('definitions', [])
                
                result += f"*{part_of_speech.upper()}*\n"
                for i, definition in enumerate(definitions[:2]):  # First 2 definitions
                    result += f"• {definition['definition']}\n"
                    if 'example' in definition:
                        result += f"  _Example: {definition['example']}_\n"
                result += "\n"
    
    return result

def format_urban_response(data, word):
    if not data.get('list'):
        return f"❌ No Urban Dictionary definition for '{word}'"
    
    result = f"💬 *Urban Dictionary: {word.upper()}*\n\n"
    first_def = data['list'][0]
    
    result += f"{first_def['definition'][:300]}...\n\n"
    if 'example' in first_def:
        result += f"*Example:* {first_def['example'][:200]}...\n"
    
    return result
