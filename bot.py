import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from function import (
    start,
    help_command,
    start_quiz,
    handle_message,
    button_callback,
    facts,
    quiz_questions,
    hero_callback  # Import hero functions from function.py
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s',
    level=logging.INFO
)

def main():
    bot_token = '7817244946:AAG6BCMlM727ywBSj4qghz18H9r1L-o_w1k'
    application = ApplicationBuilder().token(bot_token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CallbackQueryHandler(hero_callback, pattern='^(hero_random|main_menu)$'))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    logging.info("Starting bot")
    application.run_polling()

if __name__ == '__main__':
    main()