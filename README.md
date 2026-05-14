# 🛍️ Jolly Shop Bot

A fully automated Telegram shop bot with admin panel for managing products and orders.

## Features

✅ **User Features:**
- 🛒 Browse and buy products
- 💳 Binance payment integration
- 📦 Order tracking
- 🎯 Simple and intuitive interface

✅ **Admin Features:**
- ➕ Add new products
- 📝 Edit existing products
- 🗑️ Delete products
- 📋 View all orders
- 💰 Track pending payments

## Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from BotFather)
- Your Telegram User ID
- Binance ID (payment destination)

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/JHELEEL/jollyshopbot.git
cd jollyshopbot
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
```

4. **Edit `.env` file and add your credentials:**
```
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id_here
BINANCE_ID=your_binance_id_here
```

## How to Get Your Credentials

### Telegram Bot Token
1. Open Telegram and search for `@BotFather`
2. Send `/start` and follow the instructions
3. Create a new bot with `/newbot`
4. Copy the token provided

### Your Telegram User ID
1. Open Telegram and search for `@userinfobot`
2. Send any message
3. It will reply with your User ID
4. Copy this ID

### Binance ID
- Use your Binance wallet address or payment ID
- This will be displayed to customers for payment

## Running the Bot

```bash
python main.py
```

The bot will start and begin polling for updates.

## Usage

### For Customers:
1. Send `/start` to the bot
2. Click "🛒 Buy Products"
3. Select a product to see details
4. Click "✅ Payment Sent" after sending Binance payment
5. Wait for admin confirmation

### For Admin:
1. Send `/start` to the bot
2. Click "⚙️ Admin Panel"
3. Manage products:
   - ➕ Add Product: Add new items to sell
   - 📝 Edit Product: Modify existing products
   - 🗑️ Delete Product: Remove products
   - 📋 View Orders: See all customer orders
   - 📦 View Products: See all available products

## Database

The bot uses SQLite database (`shop_bot.db`) to store:
- Products (name, description, price, image URL)
- Orders (customer info, product, price, payment status, timestamps)

Database is automatically initialized on first run.

## File Structure

```
jollyshopbot/
├── main.py              # Bot entry point
├── config.py            # Configuration settings
├── database.py          # Database operations
├── handlers.py          # Message and button handlers
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
├── .env                 # Your actual credentials (add manually)
├── shop_bot.db          # SQLite database (auto-created)
└── README.md            # This file
```

## Features Details

### Product Management
- Add products with name, description, and price
- Edit product details anytime
- Delete products from catalog
- Auto-generated product IDs
- Optional image URLs for products

### Order Management
- Automatic order creation when user confirms purchase
- Order tracking with status (pending/paid)
- Customer information saved with orders
- Timestamp tracking for all orders

### Payment System
- Simple Binance ID display
- Order ID for payment reference
- Admin review system

## Troubleshooting

### Bot doesn't respond
- Check if BOT_TOKEN is correct in `.env`
- Make sure bot is running: `python main.py`
- Check internet connection

### Admin commands don't work
- Verify ADMIN_ID is your actual Telegram User ID
- Use `@userinfobot` to get your real ID

### Database errors
- Delete `shop_bot.db` if corrupted
- Bot will recreate it on next run

## Security Notes

⚠️ **Important:**
- Never share your `.env` file
- Keep your bot token private
- Use strong payment verification
- Only trust verified payment confirmations

## Support

For issues and feature requests, visit: [GitHub Issues](https://github.com/JHELEEL/jollyshopbot/issues)

## License

MIT License - Feel free to use and modify

---

**Made with ❤️ for Telegram users**
