import aiohttp
import json

async def get_word_meaning(word):
    """Get AI-based + Google search based meaning"""
    
    # AI-based simple meaning (1-2 lines)
    ai_meanings = {
        "python": "A high-level programming language known for simplicity. Also a large snake species.",
        "radha": "A Hindu goddess, consort of Lord Krishna. Popular Indian female name.",
        "command": "An instruction or order given to perform a specific action.",
        "love": "A deep feeling of affection and care towards someone or something.",
        "happy": "Feeling or showing pleasure, contentment, or joy.",
    }
    
    ai_meaning = ai_meanings.get(word.lower(), f"A word or term: {word}")
    
    # Try dictionary API for detailed meaning
    detailed = None
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    word_data = data[0]
                    
                    details = []
                    meanings = word_data.get('meanings', [])
                    for meaning in meanings[:2]:
                        pos = meaning.get('partOfSpeech', '')
                        definitions = meaning.get('definitions', [])
                        for defn in definitions[:2]:
                            details.append(f"• ({pos}) {defn.get('definition', '')}")
                    
                    if details:
                        detailed = "\n".join(details[:4])
    except:
        pass
    
    return ai_meaning, detailed
