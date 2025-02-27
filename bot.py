import logging, random
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from typing import Dict

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s',
    level=logging.INFO
)

# Данные: факты и вопросы викторины
facts = [
    {
        "text": "Великая Отечественная война — война между Советским Союзом и нацистской Германией, а также их союзниками в 1941—1945 годах.",
        "photo": "https://www.sechenov.ru/upload/medialibrary/66b/KHroniki-velikikh-strazheniy.jpeg",
        "caption": "Советские солдаты в Сталинградской битве"
    },
    {
        "text": "В ходе Великой Отечественной войны Красная армия разгромила 607 дивизий вермахта и 100 дивизий его союзников.",
        "photo": "https://www.sechenov.ru/upload/medialibrary/66b/KHroniki-velikikh-strazheniy.jpeg",
        "caption": "Советские солдаты в бою"
    },
    {
        "text": "Блокада Ленинграда длилась 872 дня и унесла жизни более 600 000 человек.",
        "photo": "https://www.sechenov.ru/upload/medialibrary/66b/KHroniki-velikikh-strazheniy.jpeg",
        "caption": "Блокадный Ленинград"
    },
    {
        "text": "Советские военнопленные в Германии были вынуждены работать на военные нужды Третьего рейха.",
        "photo": "https://www.sechenov.ru/upload/medialibrary/66b/KHroniki-velikikh-strazheniy.jpeg",
        "caption": "Советские военнопленные"
    }
]

quiz_questions = [
    {
        "question": "В каком году началась Великая Отечественная война?",
        "options": ["1939", "1941", "1942", "1940"],
        "correct": "1941"
    },
    {
        "question": "Сколько дней длилась блокада Ленинграда?",
        "options": ["872", "900", "600", "1000"],
        "correct": "872"
    },
    {
        "question": "Кто был Верховным главнокомандующим в годы ВОВ?",
        "options": ["Жуков", "Сталин", "Рокоссовский", "Ворошилов"],
        "correct": "Сталин"
    }
]

# Хелпер: возвращает уникальный факт, не повторяющийся до полного просмотра
def get_unique_fact(context: ContextTypes.DEFAULT_TYPE) -> Dict:
    if 'shown_facts' not in context.user_data:
        context.user_data['shown_facts'] = []
    if len(context.user_data['shown_facts']) >= len(facts):
        context.user_data['shown_facts'] = []
    available_facts = [f for f in facts if f not in context.user_data['shown_facts']]
    fact = random.choice(available_facts)
    context.user_data['shown_facts'].append(fact)
    return fact

# Хелпер: отправка вопроса викторины
async def send_quiz_question(send_func, context: ContextTypes.DEFAULT_TYPE) -> None:
    q_index = context.user_data['quiz_question']
    question = quiz_questions[q_index]
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"quiz_{opt}")] for opt in question['options']]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"Вопрос {q_index + 1} из {len(quiz_questions)}:\n\n{question['question']}"
    await send_func(text, reply_markup)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Received /start command")
    keyboard = [
        [KeyboardButton("Интересные факты про ВОВ 📚")],
        [KeyboardButton("Пройти викторину ✏️")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text('Привет! Я твой бот про Великую Отечественную Войну 🎖️', reply_markup=reply_markup)

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Received /help command")
    await update.message.reply_text("Доступные команды:\n/start - Начать\n/help - Помощь")

# Старт викторины (не перезадается, если уже есть данные)
async def start_quiz(update_obj, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'quiz_question' not in context.user_data:
        context.user_data['quiz_question'] = 0
        context.user_data['correct_answers'] = 0
    # Универсальный send_function: использует message.reply_text или reply_text (для callback)
    if hasattr(update_obj, 'message') and update_obj.message:
        send_func = lambda text, markup: update_obj.message.reply_text(text, reply_markup=markup)
    else:
        send_func = lambda text, markup: update_obj.reply_text(text, reply_markup=markup)
    await send_quiz_question(send_func, context)

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "Интересные факты про ВОВ 📚":
        await update.message.reply_text("Отлично! Вот интересный факт ⭐", reply_markup=ReplyKeyboardRemove())
        fact = get_unique_fact(context)
        # Если все факты просмотрены, предлагаем видео
        if len(context.user_data['shown_facts']) >= len(facts):
            await update.message.reply_text("Вы увидели все факты! Начинаем заново.")
            context.user_data['shown_facts'] = []
            keyboard = [[InlineKeyboardButton("Может посмотрим видео на Rutube", url="https://rutube.ru/video/35a4cbd19c68ebf46a344c31102a1b5f/")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("https://google.com", reply_markup=reply_markup)
            return
        keyboard = [[InlineKeyboardButton("Еще интересные факты ➡️", callback_data='more_facts')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(fact["text"], reply_markup=reply_markup)
        try:
            await update.message.reply_photo(photo=fact["photo"], caption=fact["caption"])
            logging.info("Photo sent successfully")
        except Exception as e:
            logging.error(f"Error sending photo: {e}")
            await update.message.reply_text("К сожалению, не удалось отправить фотографию")
    elif text == "Пройти викторину ✏️":
        await update.message.reply_text("Давайте проверим ваши знания о ВОВ! 🎯", reply_markup=ReplyKeyboardRemove())
        await start_quiz(update, context)
    else:
        await update.message.reply_text("Я не понимаю. Используй кнопки или команду /start 🔄")

# Обработчик callback-запросов
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'more_facts':
        fact = get_unique_fact(context)
        if len(context.user_data['shown_facts']) >= len(facts):
            await query.message.reply_text("Вы увидели все факты! Начинаем заново.")
            context.user_data['shown_facts'] = []
            keyboard = [
                [InlineKeyboardButton("Может посмотрим видео про ВОВ 🎥", url="https://rutube.ru/video/35a4cbd19c68ebf46a344c31102a1b5f/")],
                [InlineKeyboardButton("Пройти викторину про ВОВ 📝", callback_data='start_quiz')],
                [InlineKeyboardButton("Просмотреть факты заново 🔄", callback_data='restart_facts')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Вы можете посмотреть видео, пройти викторину или начать просмотр фактов заново:", reply_markup=reply_markup)
            return
        
        keyboard = [[InlineKeyboardButton("Еще интересные факты ➡️", callback_data='more_facts')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(fact["text"], reply_markup=reply_markup)
        try:
            await query.message.reply_photo(photo=fact["photo"], caption=fact["caption"])
        except Exception as e:
            logging.error(f"Error sending photo: {e}")
            await query.message.reply_text("К сожалению, не удалось отправить фотографию")
    
    elif query.data == 'restart_facts':
        context.user_data['shown_facts'] = []
        fact = get_unique_fact(context)
        keyboard = [[InlineKeyboardButton("Еще интересные факты ➡️", callback_data='more_facts')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Начинаем просмотр фактов заново!\n\n" + fact["text"], reply_markup=reply_markup)
        try:
            await query.message.reply_photo(photo=fact["photo"], caption=fact["caption"])
        except Exception as e:
            logging.error(f"Error sending photo: {e}")
            await query.message.reply_text("К сожалению, не удалось отправить фотографию")
    
    elif query.data.startswith('quiz_'):
        answer = query.data.replace('quiz_', '')
        current_question = quiz_questions[context.user_data['quiz_question']]
        if answer == current_question['correct']:
            context.user_data['correct_answers'] += 1
            await query.message.reply_text("Правильно! 🎉")
        else:
            await query.message.reply_text(f"Неправильно. Правильный ответ: {current_question['correct']}")
        context.user_data['quiz_question'] += 1
        if context.user_data['quiz_question'] < len(quiz_questions):
            question = quiz_questions[context.user_data['quiz_question']]
            keyboard = [[InlineKeyboardButton(opt, callback_data=f"quiz_{opt}")] for opt in question['options']]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                f"Вопрос {context.user_data['quiz_question'] + 1} из {len(quiz_questions)}:\n\n{question['question']}",
                reply_markup=reply_markup
            )
        else:
            score = context.user_data['correct_answers']
            total = len(quiz_questions)
            await query.message.reply_text(f"Викторина завершена!\nВаш результат: {score} из {total} правильных ответов.")
            keyboard = [
                [InlineKeyboardButton("Пройти викторину снова 🔄", callback_data='restart_quiz')],
                [InlineKeyboardButton("Посмотреть интересные факты 📚", callback_data='more_facts')],
                [InlineKeyboardButton("Посмотреть видео про ВОВ 🎥", url="https://rutube.ru/video/35a4cbd19c68ebf46a344c31102a1b5f/")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Что хотите сделать дальше?", reply_markup=reply_markup)
            context.user_data['quiz_question'] = 0
            context.user_data['correct_answers'] = 0
    
    elif query.data == 'restart_quiz':
        context.user_data['quiz_question'] = 0
        context.user_data['correct_answers'] = 0
        await start_quiz(query.message, context)
    
    elif query.data == 'start_quiz':
        context.user_data['quiz_question'] = 0
        context.user_data['correct_answers'] = 0
        question = quiz_questions[context.user_data['quiz_question']]
        keyboard = [[InlineKeyboardButton(opt, callback_data=f"quiz_{opt}")] for opt in question['options']]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            f"Вопрос {context.user_data['quiz_question'] + 1} из {len(quiz_questions)}:\n\n{question['question']}",
            reply_markup=reply_markup
        )

def main():
    bot_token = '7817244946:AAG6BCMlM727ywBSj4qghz18H9r1L-o_w1k'
    application = ApplicationBuilder().token(bot_token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logging.info("Starting bot")
    application.run_polling()

if __name__ == '__main__':
    main()