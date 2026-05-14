from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from database import (
    get_all_products, get_product, add_product, update_product, 
    delete_product, add_order, get_orders, mark_order_paid, init_db
)
from config import ADMIN_ID, CB_BUY, CB_PRODUCT, CB_CONFIRM, CB_ADMIN_MENU, CB_ADD_PRODUCT, CB_EDIT_PRODUCT, CB_DELETE_PRODUCT, CB_VIEW_ORDERS, CB_LIST_PRODUCTS, BINANCE_ID
from datetime import datetime

# Store user data for forms
user_data_store = {}

# ==================== USER HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - Show main menu"""
    init_db()
    
    user = update.effective_user
    welcome_text = f"👋 Welcome {user.first_name}!\n\nWelcome to Jolly Shop Bot! 🛍️\n\nChoose an option:"
    
    keyboard = []
    
    if user.id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("🛒 Buy Products", callback_data=CB_BUY)],
            [InlineKeyboardButton("⚙️ Admin Panel", callback_data=CB_ADMIN_MENU)]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🛒 Buy Products", callback_data=CB_BUY)]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all products for purchase"""
    query = update.callback_query
    await query.answer()
    
    products = get_all_products()
    
    if not products:
        await query.edit_message_text(text="📭 No products available yet.\n\nPlease try again later!")
        return
    
    text = "🛍️ <b>Available Products</b>\n\nSelect a product to buy:\n\n"
    
    keyboard = []
    for product in products:
        product_id, name, description, price, image_url = product
        keyboard.append([
            InlineKeyboardButton(
                f"📦 {name} - ${price}",
                callback_data=f"{CB_PRODUCT}_{product_id}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def show_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show product details and payment info"""
    query = update.callback_query
    
    # Extract product ID from callback data
    product_id = int(query.data.split('_')[1])
    
    product = get_product(product_id)
    
    if not product:
        await query.answer("Product not found!")
        return
    
    product_id, name, description, price, image_url = product
    
    text = f"""📦 <b>{name}</b>

<b>Description:</b>
{description}

<b>Price:</b> ${price}

<b>💳 Payment Details:</b>
"""
    
    if BINANCE_ID:
        text += f"\n<b>Binance ID:</b> <code>{BINANCE_ID}</code>"
        text += "\n\nSend the payment and confirm when done!"
    else:
        text += "\n⏳ <i>Binance ID will be provided by admin</i>"
    
    keyboard = []
    
    if BINANCE_ID:
        keyboard.append([
            InlineKeyboardButton("✅ Payment Sent", callback_data=f"{CB_CONFIRM}_{product_id}")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("❌ Binance ID Not Set", callback_data='back_to_products')
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=CB_BUY)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        if image_url:
            await query.edit_message_caption(
                caption=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
        else:
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
    except:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    await query.answer()

async def confirm_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm purchase and create order"""
    query = update.callback_query
    await query.answer()
    
    # Extract product ID
    product_id = int(query.data.split('_')[1])
    product = get_product(product_id)
    
    if not product:
        await query.edit_message_text(text="Product not found!")
        return
    
    product_id, name, description, price, image_url = product
    
    # Create order
    success, order_id = add_order(
        user_id=query.from_user.id,
        username=query.from_user.username or query.from_user.first_name,
        product_id=product_id,
        product_name=name,
        price=price
    )
    
    if success:
        text = f"""✅ <b>Purchase Confirmed!</b>

<b>Order Details:</b>
Order ID: <code>{order_id}</code>
Product: {name}
Amount: ${price}
Status: ⏳ Pending Payment

<b>Instructions:</b>
1. Send ${price} to the Binance ID provided
2. Wait for admin confirmation
3. You'll receive the product delivery

Thank you for shopping with us! 🛍️"""
    else:
        text = "❌ Error creating order. Please try again."
    
    keyboard = [
        [InlineKeyboardButton("🛒 Continue Shopping", callback_data=CB_BUY)],
        [InlineKeyboardButton("🏠 Home", callback_data='home')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

# ==================== ADMIN HANDLERS ====================

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel menu"""
    query = update.callback_query
    
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ You don't have permission to access admin panel", show_alert=True)
        return
    
    await query.answer()
    
    text = """⚙️ <b>Admin Panel</b>

Manage your shop:"""
    
    keyboard = [
        [InlineKeyboardButton("➕ Add Product", callback_data=CB_ADD_PRODUCT)],
        [InlineKeyboardButton("📝 Edit Product", callback_data=CB_EDIT_PRODUCT)],
        [InlineKeyboardButton("🗑️ Delete Product", callback_data=CB_DELETE_PRODUCT)],
        [InlineKeyboardButton("📋 View Orders", callback_data=CB_VIEW_ORDERS)],
        [InlineKeyboardButton("📦 View Products", callback_data=CB_LIST_PRODUCTS)],
        [InlineKeyboardButton("🏠 Home", callback_data='home')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding a new product"""
    query = update.callback_query
    
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ Permission denied", show_alert=True)
        return
    
    await query.answer()
    
    user_id = query.from_user.id
    user_data_store[user_id] = {'action': 'add_product', 'step': 1}
    
    text = "📝 <b>Add New Product</b>\n\nStep 1/4: Enter product name"
    
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data=CB_ADMIN_MENU)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input for forms"""
    user = update.effective_user
    user_id = user.id
    
    if user_id not in user_data_store:
        return
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Permission denied")
        return
    
    user_state = user_data_store[user_id]
    text = update.message.text.strip()
    
    if user_state.get('action') == 'add_product':
        step = user_state.get('step', 1)
        
        if step == 1:
            user_state['name'] = text
            user_state['step'] = 2
            await update.message.reply_text(
                "✅ Name saved!\n\nStep 2/4: Enter product description"
            )
        elif step == 2:
            user_state['description'] = text
            user_state['step'] = 3
            await update.message.reply_text(
                "✅ Description saved!\n\nStep 3/4: Enter product price (numbers only)"
            )
        elif step == 3:
            try:
                price = float(text)
                user_state['price'] = price
                user_state['step'] = 4
                await update.message.reply_text(
                    "✅ Price saved!\n\nStep 4/4: Enter image URL (or type 'skip')"
                )
            except ValueError:
                await update.message.reply_text("❌ Please enter a valid price (numbers only)")
        elif step == 4:
            image_url = text if text.lower() != 'skip' else None
            
            success, msg = add_product(
                name=user_state['name'],
                description=user_state['description'],
                price=user_state['price'],
                image_url=image_url
            )
            
            if success:
                text = f"""✅ <b>Product Added Successfully!</b>

<b>Details:</b>
Name: {user_state['name']}
Description: {user_state['description']}
Price: ${user_state['price']}"""
            else:
                text = f"❌ {msg}"
            
            keyboard = [[InlineKeyboardButton("⚙️ Admin Panel", callback_data=CB_ADMIN_MENU)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            del user_data_store[user_id]

async def view_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View all orders"""
    query = update.callback_query
    
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ Permission denied", show_alert=True)
        return
    
    await query.answer()
    
    orders = get_orders()
    
    if not orders:
        text = "📭 No orders yet"
    else:
        text = """📋 <b>All Orders</b>

"""
        for order in orders:
            order_id, user_id, username, product_name, price, status, created_at = order
            status_emoji = "⏳" if status == "pending" else "✅"
            text += f"{status_emoji} Order #{order_id}\n"
            text += f"   User: @{username}\n"
            text += f"   Product: {product_name}\n"
            text += f"   Price: ${price}\n"
            text += f"   Status: {status}\n\n"
    
    keyboard = [[InlineKeyboardButton("⚙️ Back to Admin", callback_data=CB_ADMIN_MENU)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all products for admin"""
    query = update.callback_query
    
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ Permission denied", show_alert=True)
        return
    
    await query.answer()
    
    products = get_all_products()
    
    if not products:
        text = "📭 No products yet"
    else:
        text = """📦 <b>All Products</b>

"""
        for product in products:
            product_id, name, description, price, image_url = product
            text += f"<b>{name}</b> (ID: {product_id})\n"
            text += f"   Price: ${price}\n"
            text += f"   Description: {description[:50]}...\n\n"
    
    keyboard = [[InlineKeyboardButton("⚙️ Back to Admin", callback_data=CB_ADMIN_MENU)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Go back to main menu"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    welcome_text = f"👋 Welcome {user.first_name}!\n\nWelcome to Jolly Shop Bot! 🛍️\n\nChoose an option:"
    
    keyboard = []
    
    if user.id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("🛒 Buy Products", callback_data=CB_BUY)],
            [InlineKeyboardButton("⚙️ Admin Panel", callback_data=CB_ADMIN_MENU)]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🛒 Buy Products", callback_data=CB_BUY)]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=welcome_text, reply_markup=reply_markup)
