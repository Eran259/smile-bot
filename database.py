import sqlite3
import datetime
from crypto_helper import encrypt_data, decrypt_data

DB_NAME = "shop_database.db"

# --- Database ဖန်တီးခြင်း ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # User Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            coin_balance REAL DEFAULT 0,
            role TEXT DEFAULT 'user',
            parent_id INTEGER DEFAULT NULL,
            fee_paid INTEGER DEFAULT 0,
            expire_date TIMESTAMP DEFAULT NULL,
            is_active INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Order Log Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            game_id TEXT,
            zone_id TEXT,
            item TEXT,
            coin_used REAL,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Owner Account Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS owner_account (
            id INTEGER PRIMARY KEY,
            email TEXT,
            password TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database ဖန်တီးပြီးပါပြီ")


# --- Owner Account သိမ်းဆည်းခြင်း ---
def save_owner_account(email, password):
    enc_email = encrypt_data(email)
    enc_password = encrypt_data(password)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO owner_account (id, email, password) VALUES (1, ?, ?)",
                   (enc_email, enc_password))
    conn.commit()
    conn.close()

def get_owner_account():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT email, password FROM owner_account WHERE id = 1")
    result = cursor.fetchone()
    conn.close()
    if result:
        return decrypt_data(result[0]), decrypt_data(result[1])
    return None, None


# --- User Register ---
def register_user(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (telegram_id) VALUES (?)", (telegram_id,))
    conn.commit()
    conn.close()


# --- Balance စီမံခြင်း ---
def get_balance(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT coin_balance FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def add_balance(telegram_id, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET coin_balance = coin_balance + ? WHERE telegram_id = ?", (amount, telegram_id))
    conn.commit()
    conn.close()

def deduct_balance(telegram_id, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET coin_balance = coin_balance - ? WHERE telegram_id = ?", (amount, telegram_id))
    conn.commit()
    conn.close()


# --- Order Log သိမ်းခြင်း ---
def save_order(telegram_id, game_id, zone, item, coin_used, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (telegram_id, game_id, zone_id, item, coin_used, status) VALUES (?, ?, ?, ?, ?, ?)",
        (telegram_id, game_id, zone, item, coin_used, status)
    )
    conn.commit()
    conn.close()


# --- User Active Status ---
def is_user_active(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT is_active FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] == 1 if result else False

def activate_user(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_active = 1 WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()

def deactivate_user(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_active = 0 WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()


# --- Fee စနစ် ---
def set_fee_paid(telegram_id, days=30):
    """User ကို Fee ပေးပြီးသား သတ်မှတ်ခြင်း (Auto Expire)"""
    expire_date = datetime.datetime.now() + datetime.timedelta(days=days)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET fee_paid = 1, expire_date = ? WHERE telegram_id = ?",
        (expire_date.strftime('%Y-%m-%d %H:%M:%S'), telegram_id)
    )
    conn.commit()
    conn.close()

def is_fee_paid(telegram_id):
    """User က Fee ပေးပြီးသား ဟုတ်မဟုတ် စစ်ခြင်း (Auto Expire)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT fee_paid, expire_date FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        return False

    fee_paid, expire_date = result

    if fee_paid == 0 or not expire_date:
        return False

    try:
        expire_dt = datetime.datetime.fromisoformat(expire_date)
        if datetime.datetime.now() > expire_dt:
            # Auto Expire — fee_paid = 0 ပြောင်း
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET fee_paid = 0 WHERE telegram_id = ?", (telegram_id,))
            conn.commit()
            conn.close()
            return False
        return True
    except:
        return False

def get_fee_expire_date(telegram_id):
    """User ရဲ့ Fee သက်တမ်းကုန်မယ့်ရက် ယူခြင်း"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT fee_paid, expire_date FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        return None

    fee_paid, expire_date = result

    if fee_paid == 0 or not expire_date:
        return None

    try:
        expire_dt = datetime.datetime.fromisoformat(expire_date)
        return expire_dt.strftime('%Y-%m-%d')
    except:
        return None


# ==========================================
#              STATS FUNCTIONS
# ==========================================

def get_total_users():
    """Bot မှာ ရှိတဲ့ User စုစုပေါင်း"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def get_active_users():
    """Active ဖြစ်တဲ့ User အရေအတွက်"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def get_pending_users():
    """Pending ဖြစ်တဲ့ User အရေအတွက်"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 0")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def get_fee_paid_users():
    """Fee ပေးပြီးသား User အရေအတွက်"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE fee_paid = 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def get_total_orders():
    """Order စုစုပေါင်း"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'success'")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def get_total_coin_used():
    """User တွေ သုံးလိုက်တဲ့ Coin စုစုပေါင်း"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(coin_used) FROM orders WHERE status = 'success'")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] else 0

def get_total_balance():
    """User တွေရဲ့ Balance စုစုပေါင်း"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(coin_balance) FROM users")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] else 0

def get_top_users(limit=5):
    """Balance အများဆုံး User တွေ"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT telegram_id, coin_balance FROM users ORDER BY coin_balance DESC LIMIT ?",
        (limit,)
    )
    result = cursor.fetchall()
    conn.close()
    return result


# ==========================================
#              EXPIRE CHECKER FUNCTION
# ==========================================

def get_expiring_users():
    """ဒီနေ့ သက်တမ်းကုန်မယ့် User တွေ ရှာခြင်း"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT telegram_id, expire_date FROM users WHERE fee_paid = 1 AND expire_date LIKE ?",
        (f"{today}%",)
    )
    result = cursor.fetchall()
    conn.close()
    return result


# --- Test (Run ကြည့်ဖို့) ---
if __name__ == "__main__":
    init_db()
    register_user(123456)
    print(f"User 123456 Balance: {get_balance(123456)}")
    print(f"User 123456 Active: {is_user_active(123456)}")
    print(f"User 123456 Fee Paid: {is_fee_paid(123456)}")

    activate_user(123456)
    print(f"After activate - User 123456 Active: {is_user_active(123456)}")

    set_fee_paid(123456, 30)
    print(f"After set fee - User 123456 Fee Paid: {is_fee_paid(123456)}")
    print(f"After set fee - Expire Date: {get_fee_expire_date(123456)}")

    deactivate_user(123456)
    print(f"After deactivate - User 123456 Active: {is_user_active(123456)}")

    # Stats Test
    print(f"\n📊 Stats Test:")
    print(f"Total Users: {get_total_users()}")
    print(f"Active Users: {get_active_users()}")
    print(f"Pending Users: {get_pending_users()}")
    print(f"Fee Paid Users: {get_fee_paid_users()}")
    print(f"Total Orders: {get_total_orders()}")
    print(f"Total Coin Used: {get_total_coin_used()}")
    print(f"Total Balance: {get_total_balance()}")
    print(f"Top Users: {get_top_users(5)}")

    # Expire Checker Test
    print(f"\n📅 Expire Checker Test:")
    expiring = get_expiring_users()
    print(f"Expiring Users: {expiring}")
