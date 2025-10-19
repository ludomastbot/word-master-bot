from PIL import Image, ImageDraw, ImageFont
import os
import random
from config import TEAM_COLORS

def generate_advanced_board_image(board_data, teams, mode, current_turn=None, reveal_all=False):
    # Create image
    img_width = 1000
    img_height = 800
    img = Image.new('RGB', (img_width, img_height), color='#1e1e1e')
    draw = ImageDraw.Draw(img)
    
    try:
        # Try to load font
        font_large = ImageFont.truetype("assets/fonts/NotoSans-Bold.ttf", 24)
        font_medium = ImageFont.truetype("assets/fonts/NotoSans-Bold.ttf", 18)
        font_small = ImageFont.truetype("assets/fonts/NotoSans-Bold.ttf", 14)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Color mapping
    color_map = {
        'red': '#ff4444',
        'pink': '#ff69b4',
        'orange': '#ffa500', 
        'grey': '#808080',
        'yellow': '#ffff00',
        'green': '#00ff00',
        'blue': '#4444ff',
        'maple': '#d2691e',
        'mud': '#8b4513',
        'yellowish': '#9acd32',
        'white': '#ffffff',
        'black': '#000000'
    }
    
    # Draw header
    draw.rectangle([0, 0, img_width, 80], fill='#2d2d2d')
    mode_text = f"MEDCODI - {mode.upper().replace('_', ' ')}"
    draw.text((img_width//2, 40), mode_text, fill='white', font=font_large, anchor="mm")
    
    # Draw team status
    y_offset = 100
    for team_name, team_data in teams.items():
        color = color_map.get(team_name, '#ffffff')
        remaining = len([card for card in board_data if card['color'] == team_name and not card['revealed']])
        total = team_data['cards']
        
        # Team indicator
        if current_turn == team_name:
            draw.rectangle([50, y_offset-10, img_width-50, y_offset+30], fill='#3a3a3a', outline=color, width=3)
        
        team_text = f"{team_data['color']} {team_name.upper()}: {remaining}/{total}"
        draw.text((100, y_offset), team_text, fill=color, font=font_medium)
        y_offset += 50
    
    # Draw game board (6x4 grid)
    card_width = 140
    card_height = 80
    margin = 10
    start_x = 100
    start_y = 300
    
    for i, card in enumerate(board_data):
        row = i // 6
        col = i % 6
        
        x = start_x + col * (card_width + margin)
        y = start_y + row * (card_height + margin)
        
        # Determine card color
        if reveal_all or card['revealed']:
            bg_color = color_map.get(card['color'], '#ffffff')
            text_color = '#000000' if card['color'] in ['white', 'yellow'] else '#ffffff'
        else:
            bg_color = '#4a4a4a'
            text_color = '#ffffff'
        
        # Draw card
        draw.rectangle([x, y, x+card_width, y+card_height], fill=bg_color, outline='#666666', width=2)
        
        # Draw word (handle multi-word)
        words = card['word'].split()
        if len(words) > 1:
            # Two lines for two words
            draw.text((x+card_width//2, y+card_height//2-10), words[0], 
                     fill=text_color, font=font_small, anchor="mm")
            draw.text((x+card_width//2, y+card_height//2+10), words[1], 
                     fill=text_color, font=font_small, anchor="mm")
        else:
            # Single word
            if len(card['word']) > 8:
                # Use smaller font for long words
                draw.text((x+card_width//2, y+card_height//2), card['word'], 
                         fill=text_color, font=font_small, anchor="mm")
            else:
                draw.text((x+card_width//2, y+card_height//2), card['word'], 
                         fill=text_color, font=font_medium, anchor="mm")
        
        # Draw card number
        draw.text((x+5, y+5), str(i+1), fill=text_color, font=font_small)
    
    # Draw footer
    draw.rectangle([0, img_height-60, img_width, img_height], fill='#2d2d2d')
    if current_turn:
        footer_text = f"Current Turn: {current_turn.upper()} Team"
        draw.text((img_width//2, img_height-30), footer_text, fill='white', font=font_medium, anchor="mm")
    else:
        footer_text = "GAME ENDED"
        draw.text((img_width//2, img_height-30), footer_text, fill='white', font=font_medium, anchor="mm")
    
    return img

def generate_quiz_image(question, options, correct_index):
    img = Image.new('RGB', (800, 600), color='#1e1e1e')
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("assets/fonts/NotoSans-Bold.ttf", 28)
        font_medium = ImageFont.truetype("assets/fonts/NotoSans-Bold.ttf", 20)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
    
    # Draw question
    draw.text((400, 100), "📚 QUIZ TIME", fill='#ffffff', font=font_large, anchor="mm")
    draw.text((400, 150), question, fill='#ffffff', font=font_medium, anchor="mm")
    
    # Draw options
    option_letters = ['A', 'B', 'C', 'D']
    y_start = 250
    for i, (letter, option) in enumerate(zip(option_letters, options)):
        y = y_start + i * 80
        draw.rectangle([200, y-20, 600, y+40], fill='#3a3a3a', outline='#666666', width=2)
        draw.text((220, y+10), f"{letter}.", fill='#ffffff', font=font_medium, anchor="lm")
        draw.text((250, y+10), option, fill='#ffffff', font=font_medium, anchor="lm")
    
    return img
