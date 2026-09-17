from telegram import Update, BotCommand, MenuButtonCommands, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from database import (init_db, register_user, get_balance, add_balance,
                      deduct_balance, save_order, is_user_active,
                      activate_user, deactivate_user, save_owner_account,
                      set_fee_paid, is_fee_paid, get_fee_expire_date,
                      get_total_users, get_active_users, get_pending_users,
                      get_fee_paid_users, get_total_orders, get_total_coin_used,
                      get_total_balance, get_top_users)
import sqlite3
import datetime

# ==========================================
#              CONFIGURATION
# ==========================================

TOKEN = "8782100883:AAFXK9IjJqQJgkNgjoeNIy8a8fT-kjsHh9U"
ALERT_BOT_TOKEN = "8786178876:AAHnw5u6LbLYxsg9DaqhtpJgcGUFFjilnSE"
ADMIN_ID = 5698123475

# ✅ TEST_MODE: Pydroid 3 မှာ True, Termux/VPS မှာ False
TEST_MODE = False

# ✅ Selenium Import (VPS မှာ ဖြုတ်ထားရမယ်)
from smile_one import check_player_info, recharge_diamond, redeem_code

alert_bot = Bot(token=ALERT_BOT_TOKEN)

# ==========================================
#              ITEM PRICES & NAMES
# ==========================================

ITEM_PRICES = {
    "wp": 76, "tp": 402.5, "web": 39, "meb": 196.5,
    "55": 39, "165": 116.9, "275": 187.5, "565": 385,
    "86": 61.5, "172": 122, "257": 177.5, "343": 239,
    "344": 244, "429": 299.5, "514": 355, "600": 416.5,
    "706": 480, "792": 541.5, "878": 602, "963": 657.5,
    "1049": 719, "1135": 779.5, "1220": 835, "1412": 960,
    "1584": 1082, "1755": 1199, "2195": 1453, "3688": 2424,
    "5532": 3660, "9288": 6079
}

ITEM_NAMES = {
    "wp": "Weekly Pass", "tp": "Twilight Pass",
    "web": "Weekly Elite Bundle", "meb": "Monthly Elite Bundle",
    "55": "55 Diamonds (2x)", "165": "165 Diamonds (2x)",
    "275": "275 Diamonds (2x)", "565": "565 Diamonds (2x)",
    "86": "86 Diamonds", "172": "172 Diamonds",
    "257": "257 Diamonds", "343": "343 Diamonds",
    "344": "344 Diamonds", "429": "429 Diamonds",
    "514": "514 Diamonds", "600": "600 Diamonds",
    "706": "706 Diamonds", "792": "792 Diamonds",
    "878": "878 Diamonds", "963": "963 Diamonds",
    "1049": "1049 Diamonds", "1135": "1135 Diamonds",
    "1220": "1220 Diamonds", "1412": "1412 Diamonds",
    "1584": "1584 Diamonds", "1755": "1755 Diamonds",
    "2195": "2195 Diamonds", "3688": "3688 Diamonds",
    "5532": "5532 Diamonds", "9288": "9288 Diamonds"
}


# ==========================================
#              ALERT FUNCTION
# ==========================================

async def send_alert(text):
    try:
        await alert_bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode="Markdown")
    except Exception as e:
        print(f"⚠️ Alert မပို့နိုင်ပါ: {e}")


# ==========================================
#              USER COMMANDS
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name

    register_user(user_id)

    if username:
        username_text = f"@{username}"
    else:
        username_text = "No username set"

    # --- Status စစ် ---
    if is_user_active(user_id):
        status_text = "✅ Active"
        status_note = "\n\nℹ️ To Show Features: /help"
    else:
        status_text = "❌ Not Active"
        status_note = "\n\n⚠️ သင်မှာ ခွင့်ပြုချက် မရရှိသေးပါ။ Admin ကို ဆက်သွယ်ပါ။"

    # --- ✅ Fee Type စစ် ---
    if is_fee_paid(user_id):
        fee_type = "✅ Fee User (Coin မဖြတ်)"
        expire_date = get_fee_expire_date(user_id)
        fee_note = f"\n📅 Expire: {expire_date}"
    else:
        fee_type = "❌ % User (Coin 1.5% ဖြတ်)"
        fee_note = ""

    text = (
        f"👋 Welcome {first_name}!\n"
        f"MLBB Top Up Service — Fast & Reliable. ✨\n"
        f"Thank you for using us. ✨\n\n"
        f"👤 Username: {username_text}\n"
        f"🆔 Telegram ID: {user_id}\n"
        f"⚡ Status: {status_text}\n"
        f"💎 Type: {fee_type}"
        f"{fee_note}"
        f"{status_note}"
    )
    await update.message.reply_text(text)

    if user_id != ADMIN_ID:
        alarm_text = (
            "🔔 **New User Alert!**\n\n"
            f"👤 Name: [{first_name}](tg://user?id={user_id})\n"
            f"🔗 Username: {username_text}\n"
            f"🆔 Telegram ID: `{user_id}`\n"
            f"⚡ Status: {status_text}\n"
            f"💎 Type: {fee_type}\n\n"
            f"✅ ခွင့်ပြုဖို့: `/approve {user_id}`\n"
            f"❌ ပိတ်ဖို့: `/reject {user_id}`"
        )
        await send_alert(alarm_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_active(user_id):
        await update.message.reply_text("❌ သင်မှာ ခွင့်ပြုချက် မရရှိသေးပါ။")
        return

    text = (
        "📖 **Help Menu**\n\n"
        "💎 **Recharge Diamonds:**\n"
        "• `/ml {id} {zone} {item}` - ငွေဖြည့်ရန်\n"
        "• `/check {id} {zone}` - Player Info စစ်ရန်\n"
        "• `/role {id} {zone}` - Check Server\n"
        "• `/productlist` - ပစ္စည်းစာရင်း ကြည့်ရန်\n\n"
        "💰 **Account & Wallet:**\n"
        "• `/balance` - လက်ကျန်ငွေ စစ်ရန်\n"
        "• `/redeem {code}` - Code ဖြည့်ရန်"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_active(user_id):
        await update.message.reply_text("❌ သင်မှာ ခွင့်ပြုချက် မရရှိသေးပါ။")
        return
    bal = get_balance(user_id)
    await update.message.reply_text(f"💰 သင့် Balance: 🇧🇷 BRL: {bal} 🪙")


async def products_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_active(user_id):
        await update.message.reply_text("❌ သင်မှာ ခွင့်ပြုချက် မရရှိသေးပါ။")
        return

    text = "📦 **Product List**\n\n"
    text += "**Pass**\n"
    text += "wp - 🇧🇷 BRL: 76 🪙\n"
    text += "tp - 🇧🇷 BRL: 402.5 🪙\n"
    text += "web - 🇧🇷 BRL: 39 🪙\n"
    text += "meb - 🇧🇷 BRL: 196.5 🪙\n\n"
    text += "**2x Dia**\n"
    text += "55 - 🇧🇷 BRL: 39 🪙\n"
    text += "165 - 🇧🇷 BRL: 116.9 🪙\n"
    text += "275 - 🇧🇷 BRL: 187.5 🪙\n"
    text += "565 - 🇧🇷 BRL: 385 🪙\n\n"
    text += "**Normal Dia**\n"
    text += "86 - 🇧🇷 BRL: 61.5 🪙\n"
    text += "172 - 🇧🇷 BRL: 122 🪙\n"
    text += "257 - 🇧🇷 BRL: 177.5 🪙\n"
    text += "343 - 🇧🇷 BRL: 239 🪙\n"
    text += "344 - 🇧🇷 BRL: 244 🪙\n"
    text += "429 - 🇧🇷 BRL: 299.5 🪙\n"
    text += "514 - 🇧🇷 BRL: 355 🪙\n"
    text += "600 - 🇧🇷 BRL: 416.5 🪙\n"
    text += "706 - 🇧🇷 BRL: 480 🪙\n"
    text += "792 - 🇧🇷 BRL: 541.5 🪙\n"
    text += "878 - 🇧🇷 BRL: 602 🪙\n"
    text += "963 - 🇧🇷 BRL: 657.5 🪙\n"
    text += "1049 - 🇧🇷 BRL: 719 🪙\n"
    text += "1135 - 🇧🇷 BRL: 779.5 🪙\n"
    text += "1220 - 🇧🇷 BRL: 835 🪙\n"
    text += "1412 - 🇧🇷 BRL: 960 🪙\n"
    text += "1584 - 🇧🇷 BRL: 1082 🪙\n"
    text += "1755 - 🇧🇷 BRL: 1199 🪙\n"
    text += "2195 - 🇧🇷 BRL: 1453 🪙\n"
    text += "3688 - 🇧🇷 BRL: 2424 🪙\n"
    text += "5532 - 🇧🇷 BRL: 3660 🪙\n"
    text += "9288 - 🇧🇷 BRL: 6079 🪙"

    await update.message.reply_text(text, parse_mode="Markdown")


async def check_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_active(user_id):
        await update.message.reply_text("❌ သင်မှာ ခွင့်ပြုချက် မရရှိသေးပါ။")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("အသုံးပြုပုံ: /check {id} {zone}")
        return

    game_id, zone = args[0], args[1]
    await update.message.reply_text(f"⏳ Player Info ရှာနေပါသည်...")

    if TEST_MODE:
        text = (
            "ℹ️ **Player Information**\n\n"
            f"👤 Nickname: ᶻᵉʳᵒø\n"
            f"🌍 Country Created: Myanmar\n"
            f"📍 Login Country: Myanmar\n"
            f"📅 Account Created: 18:52, 14 September 2026\n\n"
            f"🆔 ID: {game_id} ({zone})"
        )
        await update.message.reply_text(text, parse_mode="Markdown")
        return

    info, error = check_player_info(game_id, zone)

    if error:
        await update.message.reply_text(error)
        return

    text = (
        "ℹ️ **Player Information**\n\n"
        f"👤 Nickname: {info['name']}\n"
        f"🌍 Country Created: {info.get('country', 'N/A')}\n"
        f"📍 Login Country: {info.get('login_country', 'N/A')}\n"
        f"📅 Account Created: {info.get('created', 'N/A')}\n\n"
        f"🆔 ID: {game_id} ({zone})"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def ml_recharge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name

    if not is_user_active(user_id):
        await update.message.reply_text("❌ သင်မှာ ခွင့်ပြုချက် မရရှိသေးပါ။")
        return

    args = context.args
    if len(args) < 3:
        await update.message.reply_text("အသုံးပြုပုံ: /ml {id} {zone} {item}")
        return

    game_id, zone, item = args[0], args[1], args[2]

    if item not in ITEM_PRICES:
        await update.message.reply_text(f"❌ Item မမှန်ပါ။ ရနိုင်တဲ့ Item: {', '.join(ITEM_PRICES.keys())}")
        return

    cost = ITEM_PRICES[item]
    item_name = ITEM_NAMES.get(item, item)
    user_balance = get_balance(user_id)

    if user_balance < cost:
        await update.message.reply_text(
            f"❌ Balance မလုံလောက်ပါ။\n"
            f"လိုအပ်သည်: 🇧🇷 BRL: {cost} 🪙\n"
            f"သင့် Balance: 🇧🇷 BRL: {user_balance} 🪙"
        )
        return

    await update.message.reply_text(f"⏳ Player Info စစ်ဆေးနေပါသည်...")

    if TEST_MODE:
        info = {"name": "Test Player", "id": game_id}
        error = None
        success = True
        order_id = "TEST-12345"
        err = None
    else:
        info, error = check_player_info(game_id, zone)
        if not error:
            success, order_id, err = recharge_diamond(game_id, zone, item)
        else:
            success, order_id, err = False, None, None

    if error:
        await update.message.reply_text(f"❌ {error}\nID သို့မဟုတ် Zone ကို ပြန်စစ်ပါ။")
        return

    await update.message.reply_text(f"✅ Player: {info['name']}\n⏳ {item_name} ဖြည့်နေပါသည်...")

    if success:
        deduct_balance(user_id, cost)
        save_order(user_id, game_id, zone, item, cost, "success")

        await update.message.reply_text(
            f"✅ {item_name} အောင်မြင်စွာ ဖြည့်ပြီးပါပြီ!\n"
            f"💸 ကုန်ကျငွေ: 🇧🇷 BRL: {cost} 🪙\n"
            f"💰 ကျန်ငွေ: 🇧🇷 BRL: {get_balance(user_id)} 🪙"
        )

        if user_id != ADMIN_ID:
            if username:
                username_text = f"@{username}"
            else:
                username_text = "No username"

            alarm_text = (
                "💎 **Recharge Alert!**\n\n"
                f"👤 Name: [{first_name}](tg://user?id={user_id})\n"
                f"🔗 Username: {username_text}\n"
                f"🆔 Telegram ID: `{user_id}`\n\n"
                f"🎮 Game ID: `{game_id}`\n"
                f"🌍 Zone: `{zone}`\n"
                f"👤 Player: {info['name']}\n"
                f"📦 Item: **{item_name}** (`{item}`)\n"
                f"💵 Cost: **🇧🇷 BRL: {cost} 🪙**\n"
                f"🆔 Order ID: `{order_id}`\n"
                f"💰 User Balance After: 🇧🇷 BRL: {get_balance(user_id)} 🪙"
            )
            await send_alert(alarm_text)
    else:
        await update.message.reply_text(f"❌ ငွေဖြည့်မှု မအောင်မြင်ပါ။\n{err}")


async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name

    if not is_user_active(user_id):
        await update.message.reply_text("❌ သင်မှာ ခွင့်ပြုချက် မရရှိသေးပါ။")
        return

    args = context.args
    if not args:
        await update.message.reply_text("အသုံးပြုပုံ: /redeem {code}")
        return

    code = args[0]
    await update.message.reply_text(f"⏳ Code: {code} စစ်ဆေးနေပါသည်...")

    if TEST_MODE:
        if code.upper().startswith("TEST"):
            success = True
            coin_amount = 1000
            error = None
        else:
            success = False
            coin_amount = 0
            error = "Code မမှန်ပါ"
    else:
        success, coin_amount, error = redeem_code(code)

    if not success:
        await update.message.reply_text(f"❌ {error}\nကျေးဇူးပြု၍ ပြန်စမ်းပါ။")

        if user_id != ADMIN_ID:
            if username:
                username_text = f"@{username}"
            else:
                username_text = "No username"

            alarm_text = (
                "❌ **Coin Redeem Failed!**\n\n"
                f"👤 Name: [{first_name}](tg://user?id={user_id})\n"
                f"🔗 Username: {username_text}\n"
                f"🆔 Telegram ID: `{user_id}`\n\n"
                f"🎟️ Code: `{code}`\n"
                f"⚠️ Status: **Failed**\n"
                f"💰 User Balance: 🇧🇷 BRL: {get_balance(user_id)} 🪙"
            )
            await send_alert(alarm_text)
        return

    # ==========================================
    # ✅ Fee ပေးပြီးသားလား စစ်ပါ
    # ==========================================
    if is_fee_paid(user_id):
        # Fee ပေးပြီးသား — Coin မဖြတ်
        deduct_amount = 0
        final_amount = coin_amount
        expire_date = get_fee_expire_date(user_id)
        markup_text = f"Fee ပေးပြီးသား — Coin မဖြတ်\n📅 သက်တမ်းကုန်မည့်ရက်: {expire_date}"
    else:
        # Fee မပေး — 1.5% ဖြတ်
        markup_percent = 1.5
        deduct_amount = coin_amount * (markup_percent / 100)
        final_amount = coin_amount - deduct_amount
        markup_text = f"Fee မပေး — {markup_percent}% ဖြတ် ({deduct_amount} 🪙)"
    # ==========================================

    add_balance(user_id, final_amount)

    await update.message.reply_text(
        f"✅ Code: {coin_amount} 🪙 ဖြည့်ပြီးပါပြီ!\n"
        f"📉 {markup_text}\n"
        f"💰 ကျန်ငွေ: 🇧🇷 BRL: {get_balance(user_id)} 🪙"
    )

    if user_id != ADMIN_ID:
        if username:
            username_text = f"@{username}"
        else:
            username_text = "No username"

        alarm_text = (
            "💰 **Coin Redeem Alert!**\n\n"
            f"👤 Name: [{first_name}](tg://user?id={user_id})\n"
            f"🔗 Username: {username_text}\n"
            f"🆔 Telegram ID: `{user_id}`\n\n"
            f"🎟️ Code: `{code}`\n"
            f"💵 Code Amount: **🇧🇷 BRL: {coin_amount} 🪙**\n"
            f"📉 Deducted: **{deduct_amount} 🪙**\n"
            f"📋 {markup_text}\n"
            f"💰 User Balance: 🇧🇷 BRL: {get_balance(user_id)} 🪙"
        )
        await send_alert(alarm_text)

  # ==========================================
#              ADMIN COMMANDS
# ==========================================

async def approve_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != ADMIN_ID:
        await update.message.reply_text("❌ သင်သည် Admin မဟုတ်ပါ")
        return
    if not context.args:
        await update.message.reply_text("အသုံးပြုပုံ: /approve {telegram_id}")
        return
    target_id = int(context.args[0])
    activate_user(target_id)
    await update.message.reply_text(f"✅ User {target_id} ကို ခွင့်ပြုပြီးပါပြီ")
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=(
                "✅ Admin မှ ခွင့်ပြုချက်ပေးလိုက်ပါပြီ။\n"
                "📱 Menu Button နှိပ်ပြီး အသုံးပြုနိုင်ပါပြီ။"
            )
        )
    except Exception as e:
        print(f"⚠️ User ဆီ မပို့နိုင်ပါ: {e}")


async def reject_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != ADMIN_ID:
        await update.message.reply_text("❌ သင်သည် Admin မဟုတ်ပါ")
        return
    if not context.args:
        await update.message.reply_text("အသုံးပြုပုံ: /reject {telegram_id}")
        return
    target_id = int(context.args[0])
    deactivate_user(target_id)
    await update.message.reply_text(f"❌ User {target_id} ကို ပိတ်လိုက်ပါပြီ")


async def pending_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != ADMIN_ID:
        await update.message.reply_text("❌ သင်သည် Admin မဟုတ်ပါ")
        return
    conn = sqlite3.connect('shop_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id FROM users WHERE is_active = 0")
    users = cursor.fetchall()
    conn.close()
    if not users:
        await update.message.reply_text("📭 Pending User မရှိပါ")
        return
    text = "📋 **Pending Users**\n\n"
    for user in users:
        text += f"🆔 {user[0]}\n"
    text += "\n/approve {id} နဲ့ ခွင့်ပြုပါ"
    await update.message.reply_text(text, parse_mode="Markdown")


async def set_fee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != ADMIN_ID:
        await update.message.reply_text("❌ သင်သည် Admin မဟုတ်ပါ")
        return

    if len(context.args) < 1:
        await update.message.reply_text("အသုံးပြုပုံ: /setfee {user_id} {days}")
        return

    target_id = int(context.args[0])
    days = int(context.args[1]) if len(context.args) > 1 else 30

    set_fee_paid(target_id, days)

    expire_date = datetime.datetime.now() + datetime.timedelta(days=days)
    await update.message.reply_text(
        f"✅ User {target_id} ကို Fee ပေးပြီးသား သတ်မှတ်ပြီးပါပြီ\n"
        f"📅 သက်တမ်းကုန်မည့်ရက်: {expire_date.strftime('%Y-%m-%d')}"
    )


async def check_fee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != ADMIN_ID:
        await update.message.reply_text("❌ သင်သည် Admin မဟုတ်ပါ")
        return

    if not context.args:
        await update.message.reply_text("အသုံးပြုပုံ: /checkfee {user_id}")
        return

    target_id = int(context.args[0])
    if is_fee_paid(target_id):
        expire = get_fee_expire_date(target_id)
        status = f"✅ Fee ပေးပြီးသား (Coin မဖြတ်)\n📅 သက်တမ်းကုန်မည့်ရက်: {expire}"
    else:
        status = "❌ Fee မပေး (Coin % ဖြတ်)"

    await update.message.reply_text(
        f"🆔 User: `{target_id}`\n"
        f"📋 Status: {status}",
        parse_mode="Markdown"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != ADMIN_ID:
        await update.message.reply_text("❌ သင်သည် Admin မဟုတ်ပါ")
        return

    total = get_total_users()
    active = get_active_users()
    pending = get_pending_users()
    fee_paid = get_fee_paid_users()
    total_orders = get_total_orders()
    total_coins = get_total_coin_used()
    total_balance = get_total_balance()

    top_users = get_top_users(5)
    top_text = ""
    for i, (uid, bal) in enumerate(top_users, 1):
        top_text += f"{i}. `{uid}` — {bal} 🪙\n"

    text = (
        "📊 **Bot Statistics**\n\n"
        "👥 **Users:**\n"
        f"• Total Users: **{total}**\n"
        f"• Active: **{active}**\n"
        f"• Pending: **{pending}**\n"
        f"• Fee Paid: **{fee_paid}**\n\n"
        "📦 **Orders:**\n"
        f"• Total Orders: **{total_orders}**\n"
        f"• Total Coin Used: **{total_coins}** 🪙\n\n"
        "💰 **Wallet:**\n"
        f"• Total User Balance: **{total_balance}** 🪙\n\n"
        "🏆 **Top 5 Users:**\n"
        f"{top_text}"
    )

    await update.message.reply_text(text, parse_mode="Markdown")


# ==========================================
#              MENU BUTTON
# ==========================================

async def post_init(application):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show Help Menu"),
        BotCommand("balance", "Check Your Wallet"),
        BotCommand("productlist", "Check Product List"),
        BotCommand("check", "Check Player Info"),
        BotCommand("role", "Check Server"),
        BotCommand("ml", "Recharge MLBB Diamonds"),
        BotCommand("redeem", "Top Up Smile Coins"),
    ]
    await application.bot.set_my_commands(commands)
    await application.bot.set_chat_menu_button(menu_button=MenuButtonCommands())
    print("✅ Menu Button သတ်မှတ်ပြီးပါပြီ")


# ==========================================
#              MAIN
# ==========================================

def main():
    init_db()

    # ✅ Account သိမ်းပြီးသား (Comment ထည့်ထားပါ)
    # save_owner_account("thetnaingswan882@gmail.com", "Eren Yeager 25")

    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("productlist", products_list))
    app.add_handler(CommandHandler("check", check_player))
    app.add_handler(CommandHandler("role", check_player))
    app.add_handler(CommandHandler("ml", ml_recharge))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("approve", approve_user))
    app.add_handler(CommandHandler("reject", reject_user))
    app.add_handler(CommandHandler("pending", pending_users))
    app.add_handler(CommandHandler("setfee", set_fee))
    app.add_handler(CommandHandler("checkfee", check_fee))
    app.add_handler(CommandHandler("stats", stats))
    print("🤖 Bot စတင်လုပ်ဆောင်နေပါပြီ...")
    app.run_polling()


if __name__ == "__main__":
    main()
