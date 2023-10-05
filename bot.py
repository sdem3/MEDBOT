import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.types.input_file import InputFile
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from config import TOKEN, features, diabetic_polyneuropatia, domination_factors
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from keyboards import keyboardlist
from keyboards import StartKeyBoard
import sqlite3 as sq
from datetime import date


class UserState(StatesGroup):
    user_name = State()
    begin_testing = State()



bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage= MemoryStorage())
kb1 = KeyboardButton('начать')
answers = {} #user id : array with answers

patient_sex = {}
user_answer_cache = []

def to_features(i, j):  # по нашей нумерации коллбэков возвращает признак-ответ, данный пользоватлем
    sign = ''
    for sign_ in features.keys():
        if (i == 0):
            sign = sign_
            break
        i -= 1
    ans = ''
    for ans_ in features[sign].keys():
        if (j == 0):
            ans = ans_
            break
        j -= 1
    return (sign, ans)


async def send_callback_keyboard(i, j, callback_query):  # создает клавиатуру, которая повторяет ответ, введенный пользователем
    sign, ans = to_features(i, j)
    keyboard = InlineKeyboardMarkup()

    if ((i == 0) and (patient_sex[callback_query.from_user.id] == 'female') ):

        keyboard.add(InlineKeyboardButton('Далее', callback_data=f'show_{i + 2}_{j + 2}_f'.format(i, j)))

    elif ((i == 1) and (patient_sex[callback_query.from_user.id] == 'male') ):

        keyboard.add(InlineKeyboardButton('Далее', callback_data=f'show_{i + 3}_{j + 3}_f'.format(i, j)) )

    elif i < len(features) - 1:
        keyboard.add(InlineKeyboardButton('Далее', callback_data=f'show_{i + 1}_{j + 1}_f'.format(i, j)))
    else:
        keyboard.add(InlineKeyboardButton('Узнать результат', callback_data='res'))


    keyboard.add(InlineKeyboardButton('назад', callback_data=f'show_{i}_{j}_b'.format(i, j)))
    await bot.delete_message(chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id)

    await bot.send_message(callback_query.from_user.id, f'{sign}\nВаш ответ: {ans}'.format(sign, ans), reply_markup=keyboard)


@dp.message_handler(commands=['start'], state = '*')
async def process_start_command(message: types.Message):

    await UserState.user_name.set()
    await message.reply('''Здравствуйте! Этот бот предназначен для прогнозироваания вероятности падения пациента, чтобы узнать свой риск падения, введите свое ФИО и ответьте на вопросы, это не займет много времени''')
    answers[message.from_user.id] = [message.from_user.id] + 67 * ['-']


@dp.message_handler(state = UserState.user_name)
async def required_to_ans(message : types.Message, state : FSMContext):
    async with state.proxy() as data:
        data['user_name'] = message.text

    await UserState.next()
    await message.reply(f'Ваше имя:{data["user_name"]}.',  reply_markup=StartKeyBoard)


@dp.callback_query_handler(lambda c: c.data == 'error_in_name', state = UserState.begin_testing)
async def required_to_ans(callback_query: types.CallbackQuery, state : FSMContext):

    await UserState.user_name.set()

    await bot.send_message(callback_query.from_user.id, 'Введите ваше ФИО заново')



@dp.message_handler(commands=['help'])
async def process_start_command(message: types.Message):
    await message.reply('help')


@dp.callback_query_handler(lambda c: c.data[0:3] == 'res', state = UserState.begin_testing)
async def process_callback_query(callback_query: types.CallbackQuery, state : FSMContext):

    await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id, reply_markup=None)

    result = 0
    risk = ''
    i = 2
    pharma_counts = 0
    polineuropatia = 0
    domination_factors_count = 0
    print(answers[callback_query.from_user.id])
    print(len(answers[callback_query.from_user.id]))
    for name_feature in features.keys():
        string_feature = f'{name_feature}'.format(name_feature)
        ans = answers[callback_query.from_user.id][i]
        #print(string_feature, ans, sep = ':')

        if (ans != '-'):
            result += features[string_feature][ans]
        i +=1
        if (string_feature in domination_factors.keys()):
            if (ans in domination_factors[string_feature]) :
                domination_factors_count+=1
        if (string_feature in diabetic_polyneuropatia) :
            polineuropatia+=1
            result+=4

    if (polineuropatia == 4):
        result*=2

    if (domination_factors_count >=1 or result >= 101):
        risk = 'Высокий риск падений'
        photo = InputFile('highest.png')
    elif (71 <= result <= 100 ):
        risk = 'Повышенный риск падений'
        photo = InputFile('high.jpeg')
    elif (50 <= result <= 70):
        risk = 'Средний риск падений'
        photo = InputFile('average.png')
    elif (21 <= result <= 49):
        risk = 'Низкий риск падений'
        photo = InputFile('low.jpeg')
    elif (0<= result <= 20):
        risk = 'Минимальный риск падений'
        photo = InputFile('minimal.jpeg')



    data = answers[callback_query.from_user.id]
    data[len(data) - 2] = result
    data[len(data) - 1] = date.today()

    conn = sq.connect('patients.sqlite')
    cur = conn.cursor()
    cur.execute(''' INSERT INTO patients VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);''', tuple(data) )
    conn.commit()
    conn.close()

    await bot.send_photo(chat_id = callback_query.from_user.id, photo = photo, caption= f'Ваш результат:{risk}, \nКоличество баллов:{result} \n чтобы пройти тестирование еще раз введите команду: /start '.format(risk, result))
    #await bot.send_message(callback_query.from_user.id, f'Ваш результат:{risk}'.format(risk))
    await state.finish()

@dp.callback_query_handler(lambda c: c.data[0:4] == 'show', state = UserState.begin_testing)
async def process_callback_query(callback_query: types.CallbackQuery, state : FSMContext):
    text = callback_query.data.split('_')
    i = int(text[1])
    j = int(text[2])
    if (i==j==0):
        async with state.proxy() as data:
            answers[callback_query.from_user.id][1] = data["user_name"]
            print(data["user_name"])
    if text[3] == 'b':
        await bot.delete_message(chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id)
        #answers[callback_query.from_user.id].pop(len(answers[callback_query.from_user.id]) - 1)
    else:

        await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id, reply_markup=None)

    sign, ans = to_features(i, j)
    await bot.send_message(callback_query.from_user.id, sign, reply_markup=keyboardlist[i])


@dp.callback_query_handler(lambda c: c.data[0:3] == 'ans', state = UserState.begin_testing)
async def process_callback_query(callback_query: types.CallbackQuery):

    text = callback_query.data.split('_')
    i = int(text[1])
    j = int(text[2])
    sign, ans = to_features(i, j)
    print(sign, ans, sep = ',')

    if (sign ==  'Выберете свой пол'):
        if (ans == "Мужчина"):
            patient_sex[callback_query.from_user.id] = 'male'
        else:
            patient_sex[callback_query.from_user.id] = 'female'

    print(patient_sex[callback_query.from_user.id])


    '''if (i == 0  and patient_sex[callback_query.from_user.id] == 'female'):
        answers[callback_query.from_user.id].append('-')
    elif (i == 1 and patient_sex[callback_query.from_user.id] == 'male'):
        answers[callback_query.from_user.id].append(ans)
        answers[callback_query.from_user.id].append('-')
        answers[callback_query.from_user.id].append('-')
    else: '''

    answers[callback_query.from_user.id][i + 2] = ans


    if i < len(features) - 1:
        sign_next, s = to_features(i + 1, 0)
    print('!!!!!!!!!!!!!!!!!!!!!!!!!WOOOOOORK!!!!!!!!!!!!!!!!!')
    print
    print(sign, ans, i, sep='/////')
    print(answers[callback_query.from_user.id])
    # print('\n',dataset.loc[callback_query.from_user.id].values)
    await send_callback_keyboard(i, j, callback_query)


executor.start_polling(dp)
