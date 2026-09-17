from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from database import get_owner_account
import time
import random
import shutil


# ==========================================
#              CONFIGURATION
# ==========================================

# ✅ Rate Limit (Between Recharge/Redeem actions)
MIN_DELAY_BETWEEN_ACTIONS = 8   # seconds
MAX_DELAY_BETWEEN_ACTIONS = 15  # seconds

# ✅ Proxy (Optional — add later)
# Example: "http://user:pass@ip:port"
PROXY = None


# ==========================================
#              DRIVER SETUP (ANTI-BOT)
# ==========================================

def get_driver():
    """Create Chrome Driver (Anti-Bot)"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # ✅ Anti-Bot 1: Change User-Agent
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )

    # ✅ Anti-Bot 2: Disable Automation Detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # ✅ Anti-Bot 3: Proxy (Optional)
    if PROXY:
        options.add_argument(f"--proxy-server={PROXY}")

    # ✅ Chrome Binary Location (Auto Detect for GitHub Actions/VPS)
    chrome_path = (
        shutil.which("chromium") or
        shutil.which("chromium-browser") or
        shutil.which("google-chrome") or
        shutil.which("google-chrome-stable")
    )
    if chrome_path:
        options.binary_location = chrome_path
        print(f"✅ Chrome Path: {chrome_path}")
    else:
        print("⚠️ Chrome Path မတွေ့ပါ — Default သုံးမယ်")

    try:
        driver = webdriver.Chrome(options=options)

        # ✅ Anti-Bot 4: Hide WebDriver Flag
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        return driver
    except Exception as e:
        print(f"❌ Driver Error: {e}")
        return None


# ==========================================
#              HELPER FUNCTIONS
# ==========================================

def random_delay(min_sec=2, max_sec=5):
    """Random Delay (Human-like)"""
    time.sleep(random.uniform(min_sec, max_sec))


def action_delay():
    """Rate Limit Delay between Recharge/Redeem"""
    delay = random.uniform(MIN_DELAY_BETWEEN_ACTIONS, MAX_DELAY_BETWEEN_ACTIONS)
    print(f"⏳ Rate Limit: waiting {delay:.1f} seconds...")
    time.sleep(delay)


# ==========================================
#              SMILE ONE LOGIN
# ==========================================

def smile_one_login():
    """Login to Smile One Account"""
    email, password = get_owner_account()

    if not email or not password:
        print("❌ Owner Account not found")
        return None

    driver = get_driver()
    if not driver:
        return None

    try:
        print("🌐 Opening Smile One Login Page...")
        driver.get("https://www.smile.one/customer/account/accountlogin")
        random_delay(3, 5)

        # --- Enter Email ---
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "field-email"))
        )
        email_input.clear()
        email_input.send_keys(email)
        random_delay(1, 3)

        # --- Enter Password ---
        password_input = driver.find_element(By.ID, "field-password")
        password_input.clear()
        password_input.send_keys(password)
        random_delay(1, 3)

        # --- Click Login ---
        login_btn = driver.find_element(By.ID, "smileone-account-login-btn")
        login_btn.click()
        print("⏳ Login clicked...")
        random_delay(5, 8)

        # --- Check if Login Successful ---
        current_url = driver.current_url
        print(f"📍 Current URL: {current_url}")

        if "accountlogin" not in current_url:
            print("✅ Login successful")
            return driver
        else:
            print("❌ Login failed")
            driver.quit()
            return None

    except Exception as e:
        print(f"❌ Login Error: {e}")
        driver.quit()
        return None


# ==========================================
#              CHECK PLAYER INFO
# ==========================================

def check_player_info(game_id, zone):
    """
    Check Player Info
    Return: (info_dict, error_message)
    """
    driver = smile_one_login()
    if not driver:
        return None, "❌ Player ID not available yet"

    try:
        print(f"🔍 Searching Player Info: {game_id} ({zone})")

        # --- Go to Mobile Legends Page ---
        driver.get("https://www.smile.one/merchant/mobilelegends?source=smileone")
        random_delay(3, 5)

        # --- Enter Game ID ---
        id_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "user_id"))
        )
        id_input.clear()
        id_input.send_keys(game_id)
        random_delay(1, 2)

        # --- Enter Zone ---
        zone_input = driver.find_element(By.ID, "zone_id")
        zone_input.clear()
        zone_input.send_keys(zone)
        random_delay(1, 2)

        # --- Check Role (Tab) ---
        zone_input.send_keys("\t")
        random_delay(3, 5)

        # --- Read Player Name ---
        try:
            player_name = driver.find_element(By.ID, "mnickname").text
            if player_name:
                info = {"name": player_name, "id": game_id, "zone": zone}
                return info, None
            else:
                return None, "❌ Player not found (Wrong ID/Zone)"
        except:
            return None, "❌ Player Info not found"

    except Exception as e:
        return None, f"❌ Error: {e}"
    finally:
        driver.quit()


# ==========================================
#              RECHARGE DIAMOND
# ==========================================

def recharge_diamond(game_id, zone, item_id):
    """
    Recharge Diamond
    Return: (success, order_id, error_message)
    """
    # ✅ Rate Limit Delay (Human-like)
    action_delay()

    driver = smile_one_login()
    if not driver:
        return False, None, "❌ Diamond top-up not available yet"

    try:
        print(f"💎 Recharging Diamond: {game_id} ({zone}) - Item {item_id}")

        # --- Go to Mobile Legends Page ---
        driver.get("https://www.smile.one/merchant/mobilelegends?source=smileone")
        random_delay(3, 5)

        # --- Enter Game ID ---
        id_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "user_id"))
        )
        id_input.clear()
        id_input.send_keys(game_id)
        random_delay(1, 2)

        # --- Enter Zone ---
        zone_input = driver.find_element(By.ID, "zone_id")
        zone_input.clear()
        zone_input.send_keys(zone)
        random_delay(1, 2)

        # --- Check Role ---
        zone_input.send_keys("\t")
        random_delay(3, 5)

        # --- Check Player Name ---
        try:
            player_name = driver.find_element(By.ID, "mnickname").text
            if not player_name:
                return False, None, "❌ Player not found"
        except:
            return False, None, "❌ Player Info not found"

        # --- Select Item (by Product ID) ---
        try:
            item_btn = driver.find_element(By.ID, item_id)
            item_btn.click()
            print(f"✅ Item {item_id} selected")
            random_delay(2, 3)
        except:
            return False, None, f"❌ Item {item_id} not found"

        # --- Click Buy Button ---
        try:
            buy_btn = driver.find_element(By.CLASS_NAME, "Nav-btn")
            buy_btn.click()
            print("⏳ Buy Button clicked...")
            random_delay(5, 8)
        except Exception as e:
            return False, None, f"❌ Buy Button Error: {e}"

        # --- Go to Order History Page ---
        driver.get("https://www.smile.one/customer/order")
        random_delay(3, 5)

        # --- Read Order ID ---
        try:
            order_id = driver.find_element(By.CLASS_NAME, "order-id").text
        except:
            order_id = "N/A"

        return True, order_id, None

    except Exception as e:
        return False, None, f"❌ Error: {e}"
    finally:
        driver.quit()


# ==========================================
#              REDEEM CODE
# ==========================================

def redeem_code(code):
    """
    Redeem Code
    Return: (success, coin_amount, error_message)
    """
    # ✅ Rate Limit Delay (Human-like)
    action_delay()

    driver = smile_one_login()
    if not driver:
        return False, 0, "❌ Coin top-up not available yet"

    try:
        print(f"🎟️ Redeeming Code: {code}")

        # --- Go to Redeem Page ---
        driver.get("https://www.smile.one/customer/activationcode")
        random_delay(3, 5)

        # --- Enter Code ---
        code_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "activation_code"))
        )
        code_input.clear()
        code_input.send_keys(code)
        random_delay(1, 2)

        # --- Click Redeem Button ---
        redeem_btn = driver.find_element(By.CLASS_NAME, "smileone-button")
        redeem_btn.click()
        print("⏳ Redeem clicked...")
        random_delay(5, 8)

        # --- Check Result ---
        page_source = driver.page_source.lower()

        if "success" in page_source or "sucesso" in page_source:
            # Read Coin Amount
            try:
                coin_text = driver.find_element(By.CLASS_NAME, "coin-amount").text
                coin_amount = int(''.join(filter(str.isdigit, coin_text)))
            except:
                coin_amount = 0
            return True, coin_amount, None

        elif "already used" in page_source or "já foi usado" in page_source:
            return False, 0, "❌ Code already used"

        elif "expired" in page_source or "expirado" in page_source:
            return False, 0, "❌ Code expired"

        elif "invalid" in page_source or "inválido" in page_source:
            return False, 0, "❌ Invalid code"

        else:
            return False, 0, "❌ Code redeem failed"

    except Exception as e:
        return False, 0, f"❌ Error: {e}"
    finally:
        driver.quit()


# ==========================================
#              TEST (Optional)
# ==========================================

if __name__ == "__main__":
    print("🚀 Smile One Test starting...")
    print("📧 Searching Owner Account...")

    email, password = get_owner_account()

    if email:
        print(f"✅ Account found: {email}")
    else:
        print("❌ Account not found")

    print("✅ Test finished")
