from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from config import features
keyboardlist = []
i = 0
for sign in features.keys():
    keyboardlist.append(InlineKeyboardMarkup())
    j = 0
    for ans in features[sign].keys():
        keyboardlist[i].add(InlineKeyboardButton(f"{ans}".format(ans), callback_data= f"ans_{i}_{j}".format(i,j) )  )
        j+=1

    i+=1

StartKeyBoard = InlineKeyboardMarkup().add(InlineKeyboardButton('Нет, допустил ошибку в имени', callback_data= 'error_in_name'))
StartKeyBoard.add(InlineKeyboardButton('Да. Начинаем тестирование', callback_data= 'show_0_0_f'))
#StartKeyBoard.add(InlineKeyboardButton('res', callback_data= 'res'))