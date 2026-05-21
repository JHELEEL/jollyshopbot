import sqlite3
from config import DB_PATH
from datetime import datetime

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Products table
    cursor.execute('''\
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            price REAL NOT NULL,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Product accounts/logins table (NEW)
    cursor.execute('''\
        CREATE TABLE IF NOT EXISTS product_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            additional_info TEXT,
            is_used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Orders table
    cursor.execute('''\
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            payment_method TEXT DEFAULT 'binance',
            transaction_id TEXT,
            assigned_account_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            paid_at TIMESTAMP,
            delivered_at TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (assigned_account_id) REFERENCES product_accounts(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_product(name, description, price, image_url=None):
    """Add a new product"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''\
            INSERT INTO products (name, description, price, image_url)
            VALUES (?, ?, ?, ?)
        ''', (name, description, price, image_url))
        conn.commit()
        product_id = cursor.lastrowid
        conn.close()
        return True, product_id
    except sqlite3.IntegrityError:
        return False, "Product with this name already exists!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_all_products():
    """Get all products"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, description, price, image_url FROM products ORDER BY id')
    products = cursor.fetchall()
    conn.close()
    return products

def get_product(product_id):
    """Get a specific product by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, description, price, image_url FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def update_product(product_id, name=None, description=None, price=None, image_url=None):
    """Update a product"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get current product
        cursor.execute('SELECT name, description, price, image_url FROM products WHERE id = ?', (product_id,))
        current = cursor.fetchone()
        
        if not current:
            return False, "Product not found!"
        
        # Use new values or keep existing ones
        name = name or current[0]
        description = description or current[1]
        price = price or current[2]
        image_url = image_url or current[3]
        
        cursor.execute('''\
            UPDATE products 
            SET name = ?, description = ?, price = ?, image_url = ?
            WHERE id = ?
        ''', (name, description, price, image_url, product_id))
        
        conn.commit()
        conn.close()
        return True, "Product updated successfully!"
    except sqlite3.IntegrityError:
        return False, "Product name already exists!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def delete_product(product_id):
    """Delete a product"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()
        return True, "Product deleted successfully!"
    except Exception as e:
        return False, f"Error: {str(e)}"

# ==================== PRODUCT ACCOUNTS ====================

def add_product_account(product_id, username, password, email=None, additional_info=None):
    """Add login credentials for a product"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''\
            INSERT INTO product_accounts (product_id, username, password, email, additional_info)
            VALUES (?, ?, ?, ?, ?)
        ''', (product_id, username, password, email, additional_info))
        conn.commit()
        account_id = cursor.lastrowid
        conn.close()
        return True, account_id
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_product_accounts(product_id, unused_only=True):
    """Get available logins for a product"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if unused_only:
        cursor.execute('''\
            SELECT id, username, password, email, additional_info 
            FROM product_accounts 
            WHERE product_id = ? AND is_used = 0
            ORDER BY id
        ''', (product_id,))
    else:
        cursor.execute('''\
            SELECT id, username, password, email, additional_info 
            FROM product_accounts 
            WHERE product_id = ?
            ORDER BY id
        ''', (product_id,))
    
    accounts = cursor.fetchall()
    conn.close()
    return accounts

def get_account_details(account_id):
    """Get specific account details"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''\
        SELECT id, product_id, username, password, email, additional_info, is_used 
        FROM product_accounts 
        WHERE id = ?
    ''', (account_id,))
    account = cursor.fetchone()
    conn.close()
    return account

def mark_account_used(account_id):
    """Mark an account as used"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE product_accounts SET is_used = 1 WHERE id = ?', (account_id,))
        conn.commit()
        conn.close()
        return True, "Account marked as used"
    except Exception as e:
        return False, str(e)

def delete_account(account_id):
    """Delete an account"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM product_accounts WHERE id = ?', (account_id,))
        conn.commit()
        conn.close()
        return True, "Account deleted"
    except Exception as e:
        return False, str(e)

# ==================== ORDERS ====================

def add_order(user_id, username, product_id, product_name, price):
    """Add a new order"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''\
            INSERT INTO orders (user_id, username, product_id, product_name, price, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        ''', (user_id, username, product_id, product_name, price))
        conn.commit()
        order_id = cursor.lastrowid
        conn.close()
        return True, order_id
    except Exception as e:
        return False, str(e)

def get_orders(status=None):
    """Get orders, optionally filtered by status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if status:
        cursor.execute('''\
            SELECT id, user_id, username, product_name, price, status, transaction_id, created_at
            FROM orders WHERE status = ? ORDER BY created_at DESC
        ''', (status,))
    else:
        cursor.execute('''\
            SELECT id, user_id, username, product_name, price, status, transaction_id, created_at
            FROM orders ORDER BY created_at DESC
        ''')
    
    orders = cursor.fetchall()
    conn.close()
    return orders

def get_order_details(order_id):
    """Get full order details"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''\
        SELECT id, user_id, username, product_id, product_name, price, status, 
               transaction_id, assigned_account_id, created_at, paid_at, delivered_at
        FROM orders WHERE id = ?
    ''', (order_id,))
    order = cursor.fetchone()
    conn.close()
    return order

def update_order_transaction_id(order_id, transaction_id):
    """Update order with transaction ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''\
            UPDATE orders 
            SET transaction_id = ?
            WHERE id = ?
        ''', (transaction_id, order_id))
        conn.commit()
        conn.close()
        return True, "Transaction ID recorded"
    except Exception as e:
        return False, str(e)

def mark_order_paid(order_id, account_id):
    """Mark an order as paid and assign account"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''\
            UPDATE orders 
            SET status = 'paid', paid_at = CURRENT_TIMESTAMP, assigned_account_id = ?
            WHERE id = ?
        ''', (account_id, order_id))
        
        # Mark the account as used
        cursor.execute('UPDATE product_accounts SET is_used = 1 WHERE id = ?', (account_id,))
        
        conn.commit()
        conn.close()
        return True, "Order marked as paid and account assigned"
    except Exception as e:
        return False, str(e)

def mark_order_delivered(order_id):
    """Mark an order as delivered"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''\
            UPDATE orders 
            SET status = 'delivered', delivered_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (order_id,))
        conn.commit()
        conn.close()
        return True, "Order marked as delivered"
    except Exception as e:
        return False, str(e)
