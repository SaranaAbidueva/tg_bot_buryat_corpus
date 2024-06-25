from telebot import types
another_sentence = 'Отправьте другое предложение'  # оршуулжа шадахагүй. ондоо мэдуулэл
take_task = 'Беру'  # Хэхэб  Оршуулга хэдэгб
incorrect_sentence = 'Исправить опечатки и перевести'  # Буруу дурадхалга
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


def markup_button():
    markup = types.InlineKeyboardMarkup()
    button_talk = types.InlineKeyboardButton(text=translate_bua_to_ru, callback_data='bua')
    markup.add(button_talk)
    button_talk = types.InlineKeyboardButton(text=translate_ru_to_bua, callback_data='ru')
    markup.add(button_talk)
    button_talk = types.InlineKeyboardButton(text=check_translation, callback_data='check')
    markup.add(button_talk)
    return markup


def markup_take_task():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton(take_task))
    markup.add(another_sentence)
    markup.add(incorrect_sentence)
    return markup


def markup_check():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton(right))
    markup.add(wrong)
    markup.add(another_sentence)
    markup.add(incorrect_sentence)
    return markup


# def markup_start():
#     markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True, is_persistent=True)
#     markup.add(types.KeyboardButton('START'))
#     return markup
