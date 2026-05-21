from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from database import (
    get_all_products, get_product, add_product, update_product, 
    delete_product, add_order, get_orders, mark_order_paid, init_db,
    add_product_account, get_product_accounts, get_order_details, 
    update_order_transaction_id, mark_order_delivered, get_account_details
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
        # Store order info for transaction ID
        user_id = query.from_user.id
        user_data_store[user_id] = {'action': 'add_transaction_id', 'order_id': order_id}
        
        text = f"""✅ <b>Order Created!</b>

<b>Order Details:</b>
Order ID: <code>{order_id}</code>
Product: {name}
Amount: ${price}
Status: ⏳ Awaiting Payment

<b>Instructions:</b>
1. Send ${price} to the Binance ID shown earlier
2. Reply with your transaction ID (copy-paste from Binance)
3. Admin will verify and deliver your product

Reply with your Transaction ID:"""
    else:
        text = "❌ Error creating order. Please try again."
    
    keyboard = [
        [InlineKeyboardButton("🛒 Continue Shopping", callback_data=CB_BUY)],
        [InlineKeyboardButton("🏠 Home", callback_data='home')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input for forms"""
    user = update.effective_user
    user_id = user.id
    
    if user_id not in user_data_store:
        return
    
    user_state = user_data_store[user_id]
    text = update.message.text.strip()
    
    # Handle transaction ID submission
    if user_state.get('action') == 'add_transaction_id':
        order_id = user_state['order_id']
        success, msg = update_order_transaction_id(order_id, text)
        
        if success:
            response = f"""✅ <b>Transaction ID Recorded!</b>

Order ID: <code>{order_id}</code>
Transaction ID: <code>{text}</code>

Status: ⏳ Awaiting Admin Confirmation

Admin will verify your payment and deliver your product soon!

Thank you! 🎉"""
        else:
            response = f"❌ Error: {msg}"
        
        keyboard = [[InlineKeyboardButton("🏠 Home", callback_data='home')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(response, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        del user_data_store[user_id]
        return
    
    # Admin only - add product
    if user_id != ADMIN_ID:
        return
    
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
            
            success, product_id = add_product(
                name=user_state['name'],
                description=user_state['description'],
                price=user_state['price'],
                image_url=image_url
            )
            
            if success:
                user_state['product_id'] = product_id
                user_state['action'] = 'add_accounts'
                user_state['step'] = 1
                text = f"""✅ <b>Product Added!</b>

Now add login credentials for this product.

<b>Step 1/3: Enter username/email for the login</b>"""
            else:
                text = f"❌ {success}"
            
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
            return
    
    # Add product accounts/logins
    if user_state.get('action') == 'add_accounts':
        step = user_state.get('step', 1)
        product_id = user_state.get('product_id')
        
        if step == 1:
            user_state['acc_username'] = text
            user_state['step'] = 2
            await update.message.reply_text(
                "✅ Username saved!\n\nStep 2/3: Enter password for this login"
            )
        elif step == 2:
            user_state['acc_password'] = text
            user_state['step'] = 3
            await update.message.reply_text(
                "✅ Password saved!\n\nStep 3/3: Enter email (or type 'none')"
            )
        elif step == 3:
            email = text if text.lower() != 'none' else None
            
            success, account_id = add_product_account(
                product_id=product_id,
                username=user_state['acc_username'],
                password=user_state['acc_password'],
                email=email
            )
            
            if success:
                text = f"""✅ <b>Login Added!</b>

Username: {user_state['acc_username']}
Password: {user_state['acc_password']}
Email: {email or 'None'}

Want to add more logins? (Reply with 'yes' or 'no')"""
            else:
                text = f"❌ Error: {success}"
            
            keyboard = [[InlineKeyboardButton("⚙️ Admin Panel", callback_data=CB_ADMIN_MENU)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            
            user_state['action'] = 'add_more_accounts'
            del user_data_store[user_id]

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
        [InlineKeyboardButton("📋 View Pending Orders", callback_data='view_pending_orders')],
        [InlineKeyboardButton("💳 Confirm Payment", callback_data='confirm_payment')],
        [InlineKeyboardButton("📦 View Products", callback_data=CB_LIST_PRODUCTS)],
        [InlineKeyboardButton("🏠 Home", callback_data='home')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def view_pending_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View pending orders waiting for payment confirmation"""
    query = update.callback_query
    
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ Permission denied", show_alert=True)
        return
    
    await query.answer()
    
    orders = get_orders('pending')
    
    if not orders:
        text = "📭 No pending orders"
        keyboard = [[InlineKeyboardButton("⚙️ Back to Admin", callback_data=CB_ADMIN_MENU)]]
    else:
        text = """📋 <b>Pending Orders (Awaiting Payment Confirmation)</b>

"""
        keyboard = []
        for order in orders:
            order_id, user_id, username, product_name, price, status, transaction_id, created_at = order
            text += f"🆔 Order #{order_id}\n"
            text += f"   User: @{username}\n"
            text += f"   Product: {product_name}\n"
            text += f"   Price: ${price}\n"
            text += f"   Transaction ID: {transaction_id or '❌ Not provided'}\n\n"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"✅ Confirm & Deliver #{order_id}",
                    callback_data=f"approve_order_{order_id}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("⚙️ Back to Admin", callback_data=CB_ADMIN_MENU)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def approve_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve order and deliver product"""
    query = update.callback_query
    
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ Permission denied", show_alert=True)
        return
    
    await query.answer()
    
    # Extract order ID
    order_id = int(query.data.split('_')[2])
    order_details = get_order_details(order_id)
    
    if not order_details:
        await query.edit_message_text(text="❌ Order not found!")
        return
    
    order_id, user_id, username, product_id, product_name, price, status, transaction_id, assigned_account_id, created_at, paid_at, delivered_at = order_details
    
    # Get available account for this product
    accounts = get_product_accounts(product_id, unused_only=True)
    
    if not accounts:
        text = f"""❌ <b>No available logins for this product!</b>

Order: #{order_id}
Product: {product_name}

Please add more logins for this product first."""
        keyboard = [[InlineKeyboardButton("⚙️ Back to Admin", callback_data=CB_ADMIN_MENU)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        return
    
    # Get first available account
    account_id, acc_username, acc_password, acc_email, acc_info = accounts[0]
    
    # Mark order as paid
    success, msg = mark_order_paid(order_id, account_id)
    
    if success:
        # Deliver to customer via DM
        try:
            delivery_text = f"""🎉 <b>Payment Confirmed! Your Product Delivery!</b>

<b>Order ID:</b> {order_id}
<b>Product:</b> {product_name}

<b>Login Credentials:</b>
📧 <b>Username:</b> <code>{acc_username}</code>
🔑 <b>Password:</b> <code>{acc_password}</code>
"""
            if acc_email:
                delivery_text += f"📨 <b>Email:</b> <code>{acc_email}</code>\n"
            
            delivery_text += f"\n✅ Status: Delivered\n\nThank you for your purchase! 🎉"
            
            # Send delivery message to customer
            await context.bot.send_message(
                chat_id=user_id,
                text=delivery_text,
                parse_mode=ParseMode.HTML
            )
            
            # Mark order as delivered
            mark_order_delivered(order_id)
            
            # Confirm to admin
            admin_text = f"""✅ <b>Order Delivered!</b>

Order ID: {order_id}
Customer: @{username}
Product: {product_name}

Login delivered to customer successfully!"""
        except Exception as e:
            admin_text = f"""⚠️ <b>Order Marked Paid But Could Not DM Customer</b>

Order: #{order_id}
Error: {str(e)}

Please contact customer manually."""
    else:
        admin_text = f"❌ Error: {msg}"
    
    keyboard = [[InlineKeyboardButton("⚙️ Back to Admin", callback_data=CB_ADMIN_MENU)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=admin_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

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
            accounts = get_product_accounts(product_id, unused_only=False)
            text += f"<b>{name}</b> (ID: {product_id})\n"
            text += f"   Price: ${price}\n"
            text += f"   Available Logins: {len([a for a in accounts if a])}\n"
            text += f"   Description: {description[:40]}...\n\n"
    
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
