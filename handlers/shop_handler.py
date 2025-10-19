from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_manager import db_manager
from config import SHOP_ITEMS

async def advanced_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db_manager.get_user(user.id)
    
    if not user_data:
        user_data = db_manager.create_user(user.id, user.username, user.first_name, user.last_name)
    
    shop_text = f"""
🛍️ *ADVANCED SHOP SYSTEM*

💰 *Your Balance:* {user_data.coins} coins
💎 *Gems:* {user_data.gems}

*Categories Available:*
• 🍕 Food Items (Health & Energy)
• 💝 Love Items (Romance & Affection)  
• 👑 Premium Items (Prestige & Investment)
• 📦 Your Inventory
• 💰 Player Market

*Special Features:*
• Buy low, sell high in market
• Gift items to friends
• Limited time offers
• Bulk discounts available

*Use commands or buttons below!*
    """
    
    keyboard = [
        [InlineKeyboardButton("🍕 Food Shop", callback_data="shop_food"),
         InlineKeyboardButton("💝 Love Shop", callback_data="shop_love")],
        [InlineKeyboardButton("👑 Premium Shop", callback_data="shop_premium"),
         InlineKeyboardButton("📦 My Inventory", callback_data="inventory_view")],
        [InlineKeyboardButton("💰 Player Market", callback_data="market_view"),
         InlineKeyboardButton("🎁 Gift Center", callback_data="gift_center")],
        [InlineKeyboardButton("📊 My Stats", callback_data="user_stats"),
         InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_markdown(shop_text, reply_markup=reply_markup)

async def advanced_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("""
🛒 *Usage:* `/buy item_name quantity`
*Example:* `/buy pizza 2`

*Available Items:*
• pizza - 150 coins
• burger - 100 coins  
• coke - 50 coins
• chocolate - 80 coins
• icecream - 70 coins
• rose - 200 coins
• diamond_ring - 1000 coins
• teddy_bear - 300 coins
• perfume - 400 coins
• love_letter - 150 coins
        """, parse_mode='Markdown')
        return
    
    user = update.effective_user
    user_data = db_manager.get_user(user.id)
    
    if len(context.args) == 1:
        item_name = context.args[0].lower()
        quantity = 1
    else:
        item_name = context.args[0].lower()
        try:
            quantity = int(context.args[1])
        except:
            quantity = 1
    
    item_data = SHOP_ITEMS.get(item_name)
    if not item_data:
        await update.message.reply_text("❌ Item not found in shop! Use /shop to see available items.")
        return
    
    total_cost = item_data['price'] * quantity
    
    if user_data.coins < total_cost:
        await update.message.reply_text(f"❌ Not enough coins! You need {total_cost} coins but have {user_data.coins}.")
        return
    
    # Process purchase
    db_manager.update_user_coins(user.id, -total_cost)
    db_manager.add_to_inventory(user.id, item_name, quantity)
    
    await update.message.reply_text(
        f"✅ *Purchase Successful!*\n\n"
        f"🛍️ *Item:* {item_name.replace('_', ' ').title()}\n"
        f"📦 *Quantity:* {quantity}\n"
        f"💰 *Cost:* {total_cost} coins\n"
        f"💳 *Remaining Balance:* {user_data.coins - total_cost} coins\n\n"
        f"Use /inventory to view your items!",
        parse_mode='Markdown'
    )

async def advanced_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("""
💰 *Market Selling:* `/sell item_name quantity price`
*Example:* `/sell pizza 2 200`

This lists your item in the player market!
        """, parse_mode='Markdown')
        return
    
    user = update.effective_user
    
    if len(context.args) < 3:
        await update.message.reply_text("❌ Usage: /sell item_name quantity price")
        return
    
    item_name = context.args[0].lower()
    quantity = int(context.args[1])
    price = int(context.args[2])
    
    # Check if user has the item
    inventory = db_manager.get_user_inventory(user.id)
    user_items = {item.item_name: item.quantity for item in inventory}
    
    if item_name not in user_items or user_items[item_name] < quantity:
        await update.message.reply_text(f"❌ You don't have enough {item_name} to sell!")
        return
    
    # List item in market
    db_manager.add_market_listing(user.id, user.username, item_name, quantity, price)
    
    # Remove from inventory
    db_manager.remove_from_inventory(user.id, item_name, quantity)
    
    await update.message.reply_text(
        f"📈 *Item Listed in Market!*\n\n"
        f"🏷️ *Item:* {item_name.replace('_', ' ').title()}\n"
        f"📦 *Quantity:* {quantity}\n"
        f"💰 *Price:* {price} coins each\n"
        f"💵 *Total Value:* {price * quantity} coins\n\n"
        f"Use /market to view all listings!",
        parse_mode='Markdown'
    )

async def advanced_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 3:
        await update.message.reply_text("""
🎁 *Gift System:* `/gift @username item_name quantity`
*Example:* `/gift @john pizza 1`

Send gifts to your friends!
        """, parse_mode='Markdown')
        return
    
    user = update.effective_user
    recipient_username = context.args[0].replace('@', '')
    item_name = context.args[1].lower()
    quantity = int(context.args[2])
    
    # Check if user has the item
    inventory = db_manager.get_user_inventory(user.id)
    user_items = {item.item_name: item.quantity for item in inventory}
    
    if item_name not in user_items or user_items[item_name] < quantity:
        await update.message.reply_text(f"❌ You don't have enough {item_name} to gift!")
        return
    
    # Find recipient (in real implementation, you'd lookup by username)
    # For now, we'll assume the recipient exists
    
    # Transfer item
    db_manager.remove_from_inventory(user.id, item_name, quantity)
    db_manager.add_to_inventory(recipient_username, item_name, quantity)  # This would need user_id lookup
    
    await update.message.reply_text(
        f"🎁 *Gift Sent Successfully!*\n\n"
        f"👤 *To:* @{recipient_username}\n"
        f"🎁 *Item:* {item_name.replace('_', ' ').title()}\n"
        f"📦 *Quantity:* {quantity}\n\n"
        f"Spread the love! 💝",
        parse_mode='Markdown'
    )

async def show_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    inventory = db_manager.get_user_inventory(user.id)
    
    if not inventory:
        await update.message.reply_text("📦 Your inventory is empty! Use /shop to buy some items.")
        return
    
    inventory_text = "📦 *YOUR INVENTORY*\n\n"
    total_value = 0
    
    for item in inventory:
        item_data = SHOP_ITEMS.get(item.item_name, {'price': 0, 'emoji': '📦'})
        item_value = item_data['price'] * item.quantity
        total_value += item_value
        
        inventory_text += f"{item_data['emoji']} *{item.item_name.replace('_', ' ').title()}* x{item.quantity}\n"
        inventory_text += f"   Value: {item_value} coins\n\n"
    
    inventory_text += f"💰 *Total Inventory Value:* {total_value} coins"
    
    keyboard = [
        [InlineKeyboardButton("🛍️ Shop", callback_data="shop_main"),
         InlineKeyboardButton("💰 Market", callback_data="market_view")],
        [InlineKeyboardButton("🎁 Gift Items", callback_data="gift_center")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_markdown(inventory_text, reply_markup=reply_markup)

async def show_market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    market_listings = db_manager.get_market_listings()
    
    if not market_listings:
        await update.message.reply_text("🏪 Market is empty! Be the first to list an item with /sell")
        return
    
    market_text = "🏪 *PLAYER MARKET*\n\n"
    
    for listing in market_listings[:10]:  # Show first 10 listings
        item_data = SHOP_ITEMS.get(listing.item_name, {'emoji': '📦'})
        market_text += f"{item_data['emoji']} *{listing.item_name.replace('_', ' ').title()}* x{listing.quantity}\n"
        market_text += f"   💰 {listing.price} coins each | 👤 {listing.seller_name}\n"
        market_text += f"   🏷️ ID: {listing.id}\n\n"
    
    market_text += "💡 *Use:* `/buy_market listing_id quantity` to purchase!"
    
    await update.message.reply_markdown(market_text)
