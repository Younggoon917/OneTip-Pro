import logging
import os
import datetime
import asyncio
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Set this in Railway Variables

# Simulate a small in-memory database
correct_tips = 0
tip_history = {}

# Sample high-odds games for testing (replace with scraper logic later)
def get_fake_tip():
    games = [
        {"match": "Man City vs Arsenal", "tip": "Over 2.5 Goals", "odds": 1.85, "result": "win"},
        {"match": "Real Madrid vs Barcelona", "tip": "BTTS", "odds": 1.78, "result": "win"},
        {"match": "PSG vs Lyon", "tip": "PSG to Win", "odds": 1.72, "result": "lose"},
        {"match": "Juventus vs Milan", "tip": "Under 3.5 Goals", "odds": 1.80, "result": "win"},
    ]
    return random.choice(games)

def get_today_tip():
    today = str(datetime.date.today())
    if today not in tip_history:
        tip = get_fake_tip()
        tip_history[today] = tip
    return tip_history[today]

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📅 Today’s Tip", callback_data="today")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to OneTip Pro 🎯\nGet daily high-odds winning tips at 11:00AM.", reply_markup=reply_markup)

async def today_tip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tip = get_today_tip()
    msg = f"🎯 *Today’s Tip*\n\n📅 Match: {tip['match']}\n💡 Prediction: *{tip['tip']}*\n🔥 Odds: {tip['odds']}"
    await query.edit_message_text(msg, parse_mode="Markdown")

async def send_daily_tip(app):
    global correct_tips
    while True:
        now = datetime.datetime.now()
        if now.hour == 11 and now.minute == 0:
            tip = get_today_tip()
            chat_id = 7192060190  # ← your Telegram user ID
            text = f"🎯 *Today’s Tip*\n\n📅 Match: {tip['match']}\n💡 Prediction: *{tip['tip']}*\n🔥 Odds: {tip['odds']}"
            try:
                await app.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
                if tip["result"] == "win":
                    correct_tips += 1
            except Exception as e:
                print(f"Error sending tip: {e}")
            await asyncio.sleep(60)
        await asyncio.sleep(30)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = len(tip_history)
    win = correct_tips
    await update.message.reply_text(f"📊 Stats\n\n✅ Correct Tips: {win}\n📅 Total Days: {total}")

# --- Main ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(today_tip, pattern="today"))
    app.add_handler(CommandHandler("stats", stats))

    app.run_task(send_daily_tip(app))
    app.run_polling()
