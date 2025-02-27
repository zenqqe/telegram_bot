import random
import logging
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Данные для секции "Биографии героев"
heroes = [
    {
        "name": "Георгий Жуков",
        "photo": "https://upload.wikimedia.org/wikipedia/commons/4/42/Jukov_%28Portrait%29.jpg",
        "description": "Маршал Советского Союза, сыграл ключевую роль в обороне Москвы и наступлении в Берлине.",
        "achievements": "Сталинградская битва, Курская дуга, Берлинская операция"
    },
    {
        "name": "Константин Рокоссовский",
        "photo": "https://upload.wikimedia.org/wikipedia/commons/3/36/Rokossovsky%2C_Konstantin.jpg",
        "description": "Выдающийся командующий, отличавшийся умением организовать оборону и наступательные операции.",
        "achievements": "Оборона Москвы, Висло-Одерская операция"
    },
    {
        "name": "Клим Ворошилов",
        "photo": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Voroshilov_KL.jpeg",
        "description": "Один из самых популярных маршей Советского Союза, принимавший участие в Сталинградской битве.",
        "achievements": "Сталинградская битва, Курская дуга"
    }
]

def get_random_hero() -> dict:
    """Возвращает случайную карточку героя."""
    return random.choice(heroes)

# Функция для уникального выбора героя
def get_unique_hero(context: ContextTypes.DEFAULT_TYPE) -> dict:
    if 'shown_heroes' not in context.user_data:
        context.user_data['shown_heroes'] = []
    # Если все герои уже просмотрены, возвращаем None (для дальнейшей обработки)
    if len(context.user_data['shown_heroes']) >= len(heroes):
        return None
    available_heroes = [h for h in heroes if h not in context.user_data['shown_heroes']]
    chosen_hero = random.choice(available_heroes)
    context.user_data['shown_heroes'].append(chosen_hero)
    return chosen_hero

# --- Функции для основной секции бота (факты и викторина) ---
# Здесь уже должен быть реализован ваш существующий функционал (факты, викторина, и т.д.)

# --- Новая секция: Биографии героев ---
async def send_hero_info(update_obj, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправляет информацию о случайном герое с inline-кнопками: для просмотра другого героя
    или возврата в главное меню.
    """
    hero = get_unique_hero(context)
    if hero is None:
        # Если все герои просмотрены, не отправляем новый герой
        return
    # Формируем текст с информацией
    text = (
        f"👤 *{hero['name']}*\n\n"
        f"📜 *Описание:* {hero['description']}\n\n"
        f"🏅 *Достижения:* {hero['achievements']}"
    )
    # Остаётся только кнопка "Другой герой ➡️"
    keyboard = [
        [InlineKeyboardButton("Другой герой ➡️", callback_data='hero_random')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем текст и фото (используем Markdown для выделения)
    if hasattr(update_obj, 'message') and update_obj.message:
        chat_id = update_obj.message.chat_id
        await update_obj.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        try:
            await update_obj.message.reply_photo(photo=hero["photo"], caption=hero["name"])
        except Exception as e:
            logging.error(f"Error sending hero photo: {e}")
            await update_obj.message.reply_text("К сожалению, не удалось отправить фотографию")
    else:
        # Если вызов из callback
        await update_obj.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        try:
            await update_obj.reply_photo(photo=hero["photo"], caption=hero["name"])
        except Exception as e:
            logging.error(f"Error sending hero photo: {e}")
            await update_obj.reply_text("К сожалению, не удалось отправить фотографию")

async def hero_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик callback-запросов для секции "Биографии героев".
    При нажатии на кнопку 'hero_random' отправляет информацию о другом герое.
    При 'main_menu' – возвращает меню.
    """
    query = update.callback_query
    await query.answer()
    if query.data == 'hero_random':
        # Если все герои просмотрены, выводим специальную клавиатуру с 4 кнопками
        if 'shown_heroes' in context.user_data and len(context.user_data['shown_heroes']) >= len(heroes):
            keyboard = [
                [InlineKeyboardButton("Может посмотрим видео про ВОВ 🎥", url="https://rutube.ru/video/35a4cbd19c68ebf46a344c31102a1b5f/")],
                [InlineKeyboardButton("Посмотреть интересные факты 📚", callback_data='more_facts')],
                [InlineKeyboardButton("Пройти викторину про ВОВ 📝", callback_data='start_quiz')],
                [InlineKeyboardButton("Просмотреть биографии еще раз 👨‍✈️", callback_data='restart_heroes')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Вы посмотрели все биографии! Что хотите сделать дальше?", reply_markup=reply_markup)
        else:
            await send_hero_info(query.message, context)
    
    elif query.data == 'restart_heroes':
        # Сбрасываем список просмотренных героев и запускаем показ биографий заново
        context.user_data['shown_heroes'] = []
        await send_hero_info(query.message, context)

# Facts data and quiz questions for the bot
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

# Returns a unique fact per user session
def get_unique_fact(context) -> dict:
    if 'shown_facts' not in context.user_data:
        context.user_data['shown_facts'] = []
    if len(context.user_data['shown_facts']) >= len(facts):
        context.user_data['shown_facts'] = []
    available_facts = [f for f in facts if f not in context.user_data['shown_facts']]
    fact = random.choice(available_facts)
    context.user_data['shown_facts'].append(fact)
    return fact

# Sends a quiz question with an inline keyboard
async def send_quiz_question(send_func, context) -> None:
    q_index = context.user_data['quiz_question']
    question = quiz_questions[q_index]
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"quiz_{opt}")] for opt in question['options']]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"Вопрос {q_index + 1} из {len(quiz_questions)}:\n\n{question['question']}"
    await send_func(text, reply_markup)

# --- Мoved functions from bot.py ---

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Received /start command")
    keyboard = [
        [KeyboardButton("Интересные факты про ВОВ 📚")],
        [KeyboardButton("Пройти викторину ✏️")],
        [KeyboardButton("Герои войны 👨‍✈️")]
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
    if hasattr(update_obj, 'message') and update_obj.message:
        send_func = lambda text, markup: update_obj.message.reply_text(text, reply_markup=markup)
    else:
        send_func = lambda text, markup: update_obj.reply_text(text, reply_markup=markup)
    await send_quiz_question(send_func, context)

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if (text == "Интересные факты про ВОВ 📚"):
        await update.message.reply_text("Отлично! Вот интересный факт ⭐", reply_markup=ReplyKeyboardRemove())
        fact = get_unique_fact(context)
        # Если все факты просмотрены, предлагаем варианты
        if len(context.user_data['shown_facts']) >= len(facts):
            await update.message.reply_text("Вы увидели все факты! Начинаем заново.")
            context.user_data['shown_facts'] = []
            keyboard = [
                [InlineKeyboardButton("Может посмотрим видео про ВОВ 🎥", url="https://rutube.ru/video/35a4cbd19c68ebf46a344c31102a1b5f/")],
                [InlineKeyboardButton("Просмотреть биографии 👨‍✈️", callback_data='hero_random')],
                [InlineKeyboardButton("Пройти викторину про ВОВ 📝", callback_data='start_quiz')],
                [InlineKeyboardButton("Посмотреть факты заново 🔄", callback_data='restart_facts')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Что хотите сделать дальше?", reply_markup=reply_markup)
            return
        keyboard = [[InlineKeyboardButton("Еще интересные факты ➡️", callback_data='more_facts')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(fact["text"], reply_markup=reply_markup)
        try:
            await update.message.reply_photo(photo=fact["photo"], caption=fact["caption"])
        except Exception as e:
            logging.error(f"Error sending photo: {e}")
            await update.message.reply_text("К сожалению, не удалось отправить фотографию")
    elif text == "Пройти викторину ✏️":
        await update.message.reply_text("Давайте проверим ваши знания о ВОВ! 🎯", reply_markup=ReplyKeyboardRemove())
        await start_quiz(update, context)
    elif text == "Герои войны 👨‍✈️":
        # Запуск секции биографий
        await send_hero_info(update, context)
    else:
        await update.message.reply_text("Я не понимаю. Используй кнопки или команду /start 🔄")

# Обработчик callback-запросов
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'more_facts':
        # Если все факты уже были показаны, выводим специальную клавиатуру
        if 'shown_facts' in context.user_data and len(context.user_data['shown_facts']) >= len(facts):
            await query.message.reply_text("Вы увидели все факты! Начинаем заново.")
            # Не сбрасываем сразу – сначала предлагаем варианты дальнейших действий
            keyboard = [
                [InlineKeyboardButton("Может посмотрим видео про ВОВ 🎥", url="https://rutube.ru/video/35a4cbd19c68ebf46a344c31102a1b5f/")],
                [InlineKeyboardButton("Просмотреть биографии 👨‍✈️", callback_data='hero_random')],
                [InlineKeyboardButton("Пройти викторину про ВОВ 📝", callback_data='start_quiz')],
                [InlineKeyboardButton("Посмотреть факты заново 🔄", callback_data='restart_facts')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Что хотите сделать дальше?", reply_markup=reply_markup)
            return
        # Если факты ещё не просмотрены, отправляем следующий факт
        fact = get_unique_fact(context)
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
                [InlineKeyboardButton("Просмотреть биографии 👨‍✈️", callback_data='hero_random')],
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

