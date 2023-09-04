import pandas as pd
import sqlite3 as sq

import os
from data import dataset
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
        keyboardlist[i].add(InlineKeyboardButton(f"{ans}".format(ans), callback_data=f"{i}_{j}".format(i, j)))
        j += 1

    i += 1
features_names = {x : {} for x in features.keys() }


database = pd.DataFrame(data = features_names)

data = [999, 'ddd', 'Мужчина', 'Да', '-', '-', 'более одного', '70-80', 'без переломов', 'нет', 'да', 'в течении 10 лет и ранее', 'АД на фне терапии не выше 160/90 мм рт ст ', 'в течениие 10 лет и ранее', 'редко', 'да', '2 сустава', 'да', 'да', 'да', 'До 5', '5-10 лет', 'да', 'да', 'да', 'да', 'дефицит', 'норма', 'норма', 'норма', 'ниже 15', '9.9 - 7.5', 'да', 'да', 'да', 'часто', '2 стадия', 'да', 'да', 'да', 'в анамнезе', 'да', 'да', 'нет', 'нет', 'нет', 'нет', 'нет', 'да', 'да', 'Метилдоп', 'Если ночные позывы', 'нет', 'нет', 'нет', 'нет', 'нет', 'да', 'нет', 'С опорой', 'С опорой', 'С опорой', '3 стадия', '3 стадия', '3 стадия', 'Менее 5', 100]
print(len(data))
database.head()
conn = sq.connect('patients.sqlite')
cur = conn.cursor()
data = tuple(data)
cur.execute("create table if not exists contacts (name, id)")
cur.execute("INSERT INTO contacts (name,id) values(?,?)", ('1','2'))


cur.execute("INSERT INTO patients VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", data)
#conn.commit()
print(cur.execute("pragma table_info(patients);").fetchall())/

cur = conn.cursor()

#cur.execute(''' INSERT INTO patients VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);''', answers[callback_query.from_user.id])
#database.to_sql('patients', conn, if_exists='replace', index= False)

conn.close()
