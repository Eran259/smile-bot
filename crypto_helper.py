from cryptography.fernet import Fernet
import base64
import hashlib

# ==========================================
#              ENCRYPTION KEY
# ==========================================

# ⚠️ ဒီ Key ကို ဘယ်တော့မှ မပြောင်းပါနဲ့
# Key ပြောင်းရင် Database ထဲက Encrypted Data တွေ အကုန် ဖတ်လို့ မရတော့ဘူး

SECRET_KEY = "smile_one_bot_secret_key_2026_eren"

# Fernet Key ဖန်တီးခြင်း
def get_fernet_key():
    """SECRET_KEY ကနေ Fernet Key ဖန်တီးခြင်း"""
    key_bytes = SECRET_KEY.encode()
    hashed = hashlib.sha256(key_bytes).digest()
    return base64.urlsafe_b64encode(hashed)


# ==========================================
#              ENCRYPT / DECRYPT
# ==========================================

def encrypt_data(data):
    """Data ကို Encrypt လုပ်ခြင်း"""
    if not data:
        return None
    try:
        fernet = Fernet(get_fernet_key())
        encrypted = fernet.encrypt(data.encode())
        return encrypted.decode()
    except Exception as e:
        print(f"❌ Encrypt Error: {e}")
        return None


def decrypt_data(encrypted_data):
    """Encrypted Data ကို Decrypt လုပ်ခြင်း"""
    if not encrypted_data:
        return None
    try:
        fernet = Fernet(get_fernet_key())
        decrypted = fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception as e:
        print(f"❌ Decrypt Error: {e}")
        return None


# ==========================================
#              TEST (Optional)
# ==========================================

if __name__ == "__main__":
    print("🚀 Crypto Helper Test starting...")

    # Test Data
    test_email = "thetnaingswan882@gmail.com"
    test_password = "Eren Yeager 25"

    print(f"📧 Original Email: {test_email}")
    print(f"🔑 Original Password: {test_password}")

    # Encrypt
    enc_email = encrypt_data(test_email)
    enc_password = encrypt_data(test_password)

    print(f"\n🔒 Encrypted Email: {enc_email}")
    print(f"🔒 Encrypted Password: {enc_password}")

    # Decrypt
    dec_email = decrypt_data(enc_email)
    dec_password = decrypt_data(enc_password)

    print(f"\n🔓 Decrypted Email: {dec_email}")
    print(f"🔓 Decrypted Password: {dec_password}")

    if dec_email == test_email and dec_password == test_password:
        print("\n✅ Test Passed!")
    else:
        print("\n❌ Test Failed!")

    print("✅ Test finished")
