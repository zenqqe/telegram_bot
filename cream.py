import logging
from telegram import Update,InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Инициализируем счетчик попыток, если его еще нет
    if 'attempts' not in context.user_data:
        context.user_data['attempts'] = 2

    keyboard = [
        [KeyboardButton("Кадыров"), KeyboardButton("Никита"), KeyboardButton('Тупой негр'), KeyboardButton('Kanye West')]
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )
    await update.message.reply_text(f"Как зовут YE? (Осталось попыток: {context.user_data['attempts']})", reply_markup=reply_markup)

async def opros(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Received /opros command")
    keyboard = [
        [KeyboardButton("Я готов пройти этот тест")]
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,  # Подгоняет размер кнопок под текст
    )
    await update.message.reply_text("Насколько хорошо ты знаешь YE?", reply_markup=reply_markup)

    # Создаем отдельный обработчик для ответа пользователя
    if update.message and update.message.text == "Я готов пройти этот тест":
        await quiz(update, context)


async def no(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Received /no command")
    await update.message.reply_text("Иди нахуй")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Received /start command")
    await update.message.reply_text("Я YE, я должен узнать кто ты на самом деле")
    keyboard = [
    [KeyboardButton("ДА✅"), KeyboardButton("НЕТ⭕")]
]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,  # Подгоняет размер кнопок под текст
        one_time_keyboard=True,  # Скрывает клавиатуру после использования
        input_field_placeholder = 'Выбери ДА✅ или НЕТ⭕'
)
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('ТЫ НАЦИСТ?', reply_markup=reply_markup)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Received /reset command")
    if 'choice_made' in context.user_data:
        del context.user_data['choice_made']
        await update.message.reply_text("Твой выбор сброшен. Можешь начать заново с командой /start")
    else:
        await update.message.reply_text("Ты еще не сделал выбор")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Received button")
    text = update.message.text
    # Проверяем текущий выбор
    if text == "ДА✅":
        await update.message.reply_text("Ты наш слон")
        context.user_data['choice_made'] = 'yes'
        await update.message.reply_text("Ты можешь сбросить свой выбор командой /reset")
        await update.message.reply_text(
            "Начинаем опрос...",
            reply_markup=ReplyKeyboardRemove()  # Удаляем клавиатуру
        )
        await opros(update, context)
    elif text == "Я готов пройти этот тест":
        await quiz(update, context)
    if text == "Кадыров" or text == "Никита" or text == "Тупой негр":
        context.user_data['attempts'] -= 1
        if context.user_data['attempts'] > 0:
            await update.message.reply_text(f"Нет, даю тебе еще попытку. Осталось попыток: {context.user_data['attempts']}")
            await quiz(update, context)
        else:
            await update.message.reply_text("Попытки закончились. Правильный ответ: Kanye West")
            context.user_data['attempts'] = 2  # Сбрасываем счетчик
            
    elif text == "Kanye West":
        await update.message.reply_text("Правильно! Ты достоин быть фанатом YE")
        context.user_data['attempts'] = 2  # Сбрасываем счетчик
            
    elif text == "НЕТ⭕":
        await update.message.reply_text("Иди нахуй")
        context.user_data['choice_made'] = 'no'
        await update.message.reply_text("Ты можешь сбросить свой выбор командой /reset")
    elif context.user_data.get('choice_made'):
        # Отвечаем в зависимости от предыдущего выбора
        if context.user_data['choice_made'] == 'no':
            await no(update, context)      
    else:
        # Если выбор не сделан, просим сделать выбор
        await update.message.reply_text("Сначала выбери ДА✅ или НЕТ⭕")


 
print('Bot started')

def main():
    logging.info("Starting bot")
    bot_token = '5236284091:AAGpGuqoRgvmXt-ZqHYdR0yN_fOKOpmovKQ'
    application = ApplicationBuilder().token(bot_token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button))
    application.add_handler(CommandHandler('reset', reset))
    application.add_handler(CommandHandler('orpos', opros))
    application.add_handler(CommandHandler('quiz', quiz))
    logging.info("Running polling")
    application.run_polling()

if __name__ == '__main__':
    main()