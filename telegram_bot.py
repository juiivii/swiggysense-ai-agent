from telegram.ext import Updater, MessageHandler, Filters
from dotenv import load_dotenv
import os
from agent import handle_user_query
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def handle_message(update, context):
    user_text = update.message.text
    response = handle_user_query(user_text)
    update.message.reply_text(response)

def start_bot():
    print("Bot started...")
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()