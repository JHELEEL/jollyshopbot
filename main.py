#!/usr/bin/env python3
"""
Telegram Shop Bot - Main Entry Point
A fully automated shop bot with admin panel and delivery system
"""

import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from config import BOT_TOKEN
from handlers import (
    start,
    show_products,
    show_product_details,
    confirm_purchase,
    admin_menu,
    add_product_start,
    handle_text_input,
    view_pending_orders,
    approve_order,
    list_products,
    back_to_menu,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in .env file")
        return
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))

    # Callback query handlers
    application.add_handler(CallbackQueryHandler(show_products, pattern='buy'))
    application.add_handler(CallbackQueryHandler(show_product_details, pattern=r'^product_\d+$'))
    application.add_handler(CallbackQueryHandler(confirm_purchase, pattern=r'^confirm_\d+$'))
    application.add_handler(CallbackQueryHandler(admin_menu, pattern='admin_menu'))
    application.add_handler(CallbackQueryHandler(add_product_start, pattern='add_product'))
    application.add_handler(CallbackQueryHandler(view_pending_orders, pattern='view_pending_orders'))
    application.add_handler(CallbackQueryHandler(approve_order, pattern=r'^approve_order_\d+$'))
    application.add_handler(CallbackQueryHandler(list_products, pattern='list_products'))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern='home'))
    application.add_handler(CallbackQueryHandler(show_products, pattern='back_to_products'))

    # Text message handler (for form inputs)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

    # Start the Bot
    logger.info("🤖 Bot started! Polling for updates...")
    application.run_polling()

if __name__ == '__main__':
    main()
