import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
BINANCE_ID = os.getenv('BINANCE_ID', '')

# Database
DB_PATH = 'shop_bot.db'

# Callback data prefixes
CB_BUY = 'buy'
CB_PRODUCT = 'product'
CB_CONFIRM = 'confirm'
CB_ADMIN_MENU = 'admin_menu'
CB_ADD_PRODUCT = 'add_product'
CB_EDIT_PRODUCT = 'edit_product'
CB_DELETE_PRODUCT = 'delete_product'
CB_VIEW_ORDERS = 'view_orders'
CB_LIST_PRODUCTS = 'list_products'
