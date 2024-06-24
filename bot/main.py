from telebot import TeleBot, types
import psycopg2
import os
from dotenv import load_dotenv
from markups import markup_button, markup_check, markup_take_task
from CRUD3 import get_sentence, update_translation, \
    get_count_all_sentences, get_count_bua_sentences, get_count_ru_sentences, get_count_users, \
    get_count_checked, insert_two_sentences, mark_sentence_incorrect

load_dotenv()
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
TELEBOT_TOKEN = os.getenv("TELEBOT_TOKEN")

another_sentence = 'Не могу перевести. Получить другое предложение'  # оршуулжа шадахагүй. ондоо мэдуулэл
take_task = 'Беру'  # Хэхэб  Оршуулга хэдэгб
incorrect_sentence = 'Некорректное предложение'  # Буруу дурадхалга
translate_pls = 'Введите перевод'  # Оршуулагта
right = 'Правильно'  # зүбөөр
wrong = 'Неправильно'  # буруугаар
thanks_msg = 'Спасибо, ответ записан! Чтобы перевести или проверить следующее предложение, нажмите одну из кнопок ниже'
# hайн даа
translate_ru_to_bua = 'Перевести с русского на бурятский'  # ород буряад оршуулха Ородоhоо буряад хэлэндэ оруулха
translate_bua_to_ru = 'Перевести с бурятского на русский'  # буряад ород оршуулха  Буряадайхиhаа ород болгохо
check_translation = 'Проверить перевод'
correct_pls_ru = 'Введите исправленное предложение на русском'
correct_pls_bua = 'Введите исправленное предложение на бурятском'


conn = psycopg2.connect(
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST)
conn.autocommit = True
print('Подключено')
cursor = conn.cursor()

bot = TeleBot(TELEBOT_TOKEN)
bot.set_my_commands([
    types.BotCommand(command='start', description='Начать'),
    types.BotCommand(command='help', description='Описание'),
    types.BotCommand(command='stats', description='Статистика')
])
commands = ('/start', '/help', '/stats')


@bot.message_handler(commands=['start'])
def start_bot(message):
    first_message = f"""<b>{message.from_user.first_name}</b>, сайн байна! Би шамда туһалха гуйлта.\n\
    \n<b>{message.from_user.first_name}</b>, привет! Прошу тебя помочь перевести предложения на бурятский язык.\
    \nЭто поможет улучшить машинный перевод бурятского языка.\
    \nПодробнее: /help \
    \nЕсли потерялись: /start\
    \nЧтобы начать, нажми одну из кнопок ниже:"""
    bot.send_message(message.chat.id, first_message, parse_mode='html', reply_markup=markup_button())


@bot.message_handler(commands=['help'])
def help_bot(message):
    help_message = f"""Цель этого бота - собрать параллельный корпус бурятского языка. Т.е. большой набор предложений, \
где каждому предложению на бурятском сопоставлен перевод на русский, или наоборот.\
\nТакой корпус нужен для того, чтобы сделать машинный переводчик бурятского языка. \
А также чтобы создатели больших языковых моделей (таких как ChatGPT) могли обучить модель разговаривать \
на бурятском языке.
\nВсё это поможет оцифровать и сохранить бурятский язык в электронном виде.
\n\n<a href="https://techno.yandex.ru/machine-translation/on-small-languages">Как яндекс сделал переводчик для \
якутского</a>
\nЕсли есть вопросы или предложения, пишите @sarana_a
    """
    bot.send_message(message.chat.id, help_message, parse_mode='html', reply_markup=markup_button())
    help_message_2 = f"""Бот отправит вам сообщение, либо на русском, либо на бурятском языке. \
Затем вы можете выбрать, взяться за перевод или попросить другое предложение, если это оказалось сложным. \
Если решили перевести, нажмите кнопку и введите перевод. \
\nПредложения взяты из разных источников, в том числе Википедия, библия. Поэтому некоторые предложения могут \
быть сложными для перевода.
"""


@bot.message_handler(commands=['stats'])
def stats(message):
    cursor.execute(get_count_all_sentences())
    data_all = cursor.fetchall()
    cursor.execute(get_count_bua_sentences())
    data_bua = cursor.fetchall()
    cursor.execute(get_count_ru_sentences())
    data_ru = cursor.fetchall()
    cursor.execute(get_count_users())
    data_users = cursor.fetchall()
    cursor.execute(get_count_checked())
    data_checked = cursor.fetchall()
    bot.send_message(
        message.chat.id,
        f'Всего переведено предложений: {data_all[0][0]}\
        \nПереведено с русского на бурятский: {data_bua[0][0]}\
        \nПереведено с бурятского на русский: {data_ru[0][0]}\
        \nПроверено предложений: {data_checked[0][0]}\
        \nСколько людей поучаствовало в переводе: {data_users[0][0]}\
        ')


@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document', 'location', 'contact', 'sticker'])
def none_text_handler(message):
    bot.send_message(message.chat.id, 'Отправьте текстовое сообщение или нажмите одну из кнопок')


@bot.callback_query_handler(func=lambda call: call.data == "ru")
def ru_reply_handler(call):
    send_sentence(call.message, lang='ru')


@bot.callback_query_handler(func=lambda call: call.data == "bua")
def bua_reply_handler(call):
    send_sentence(call.message, lang='bua')


@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_reply_handler(call):
    send_sentence(call.message, lang='both')


def send_sentence(message, lang):
    cursor.execute(get_sentence(lang=lang, user_id=message.chat.id))
    data = cursor.fetchall()
    if data:
        if lang == 'ru':
            bot.send_message(
                message.chat.id,
                "предложение на русском:")
            send_sentence_msg = bot.send_message(
                message.chat.id,
                f"{data[0][0]}",
                reply_markup=markup_take_task())
            sentence_id = data[0][1]
            which_corpus = data[0][2]
            bot.register_next_step_handler(send_sentence_msg, handle_answer_button, sentence_id, which_corpus, lang)
        elif lang == 'bua':
            bot.send_message(
                message.chat.id,
                "предложение на бурятском:")
            send_sentence_msg = bot.send_message(
                message.chat.id,
                f"{data[0][0]}",
                reply_markup=markup_take_task())
            sentence_id = data[0][1]
            which_corpus = data[0][2]
            bot.register_next_step_handler(send_sentence_msg, handle_answer_button, sentence_id, which_corpus, lang)
        elif lang == 'both':
            bot.send_message(
                message.chat.id,
                "Предложение на русском:")
            bot.send_message(
                message.chat.id,
                f"{data[0][1]}")
            bot.send_message(
                message.chat.id,
                "Перевод на бурятский:")
            send_sentence_msg = bot.send_message(
                message.chat.id,
                f"{data[0][0]}",
                reply_markup=markup_check())

            which_corpus = data[0][2]
            sentence_id = data[0][3]
            bot.register_next_step_handler(send_sentence_msg, handle_answer_button, sentence_id, which_corpus, lang)
    else:
        bot.send_message(message.chat.id, "Предложения закончились, скоро добавим новые")
        bot.send_message(421890176, f"Предложения {lang} закончились")


def handle_answer_button(message, sentence_id, which_corpus, lang):
    if message.text == another_sentence:
        send_sentence(message, lang=lang)
    elif message.text == take_task:
        my_ans = bot.send_message(message.chat.id, translate_pls)
        bot.register_next_step_handler(my_ans, log_translation, sentence_id=sentence_id, user_id=message.chat.id,
                                       lang=lang)
    elif message.text == right:
        bot.send_message(message.chat.id, thanks_msg, reply_markup=markup_button())
        cursor.execute(update_translation(sentence='', sentence_id=sentence_id, user_id=message.chat.id, lang=lang,
                                          boolean=True))
    elif message.text == wrong:
        cursor.execute(update_translation(sentence='', sentence_id=sentence_id, user_id=message.chat.id, lang=lang,
                                          boolean=False))
        ans = bot.send_message(message.chat.id, 'Введите предложение на русском (при необходимости исправьте)')
        bot.register_next_step_handler(ans, wrong_handler_ru, which_corpus, message.chat.id)

    elif message.text == incorrect_sentence:
        cursor.execute(mark_sentence_incorrect(sentence_id, message.chat.id))
        if lang == 'ru':
            correct_pls = bot.send_message(message.chat.id, correct_pls_ru)
            bot.register_next_step_handler(correct_pls, send_translate_pls, message.chat.id, which_corpus, lang)
        elif lang == 'bua':
            correct_pls = bot.send_message(message.chat.id, correct_pls_bua)
            bot.register_next_step_handler(correct_pls, send_translate_pls, message.chat.id, which_corpus, lang)
        elif lang == 'both':
            correct_pls = bot.send_message(message.chat.id, correct_pls_ru)
            bot.register_next_step_handler(correct_pls, wrong_handler_ru, which_corpus, message.chat.id)

    # Когда хочется не тыкая "беру" отправить перевод.
    elif message.text not in commands and lang in ('ru', 'bua'):
        log_translation(message, sentence_id, message.chat.id, lang)


def log_translation(message, sentence_id, user_id, lang):
    bot.send_message(message.chat.id, thanks_msg, reply_markup=markup_button())
    sentence = message.text
    cursor.execute(update_translation(sentence=sentence, sentence_id=sentence_id, user_id=user_id, lang=lang))


def send_translate_pls(message, user_id, which_corpus, lang):
    sentence = message.text
    ans = bot.send_message(message.chat.id, translate_pls)
    bot.register_next_step_handler(ans, log_corrected_sentences, sentence, message.chat.id, which_corpus, lang)


def log_corrected_sentences(message, sentence, user_id, which_corpus, lang):
    if lang == 'ru':
        cursor.execute(insert_two_sentences(sentence_ru=sentence, sentence_bua=message.text,
                                            which_corpus=which_corpus + '_edited', user_id=user_id))
    elif lang == 'bua':
        cursor.execute(insert_two_sentences(sentence_ru=message.text, sentence_bua=sentence,
                                            which_corpus=which_corpus + '_edited', user_id=user_id))
    bot.send_message(message.chat.id, thanks_msg, reply_markup=markup_button())


def wrong_handler_ru(message, which_corpus, user_id):
    sentence = message.text
    ans = bot.send_message(message.chat.id, 'Введите предложение на бурятском (при необходимости исправьте)')
    bot.register_next_step_handler(ans, wrong_handler_bua, sentence, user_id, which_corpus)


def wrong_handler_bua(message, sentence_ru, user_id, which_corpus):
    sentence_bua = message.text
    cursor.execute(insert_two_sentences(sentence_ru, sentence_bua, which_corpus, user_id))
    bot.send_message(message.chat.id, thanks_msg, reply_markup=markup_button())


bot.infinity_polling()
