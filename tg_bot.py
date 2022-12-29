import requests.utils
import telebot
import sqlite3

conn = sqlite3.connect('/Users/natala/PycharmProjects/untitled/dbs/botdb.db', check_same_thread=False)
cursor = conn.cursor()


def create_inline_keyboard(dict_buttons, row_width=1):
    markup = telebot.types.InlineKeyboardMarkup()
    cnt = 0
    v = []
    for k in dict_buttons.keys():
        v.append(telebot.types.InlineKeyboardButton(dict_buttons[k], callback_data=k))
        cnt += 1
        if cnt == row_width:
            markup.row(*v)
            cnt = 0
            v = []
    return markup


token = '1846456342:AAGDxzfadV7pMcA2jWwbk65IWmhQrsOK7Bk'
bot = telebot.TeleBot(token)

# переменные для расчета
weight = 65
real_age = 20
k_lifestyle = 0
k_water = 32
k_kkal = 0
sleeptime = 7.5
kostil = 0


# формула рассчета ккал по харрису бенедикту (10*weight + 1065 - 5*age + k_kkal) * k_lifestyle
# формула для рассчета сна
# формула для рассчета воды k_water*weight*k_lifestyle

def get_info(user_id: int, table: str):
    cursor.execute("SELECT * FROM " + table + " Where user_id = " + str(user_id))
    return list(cursor.fetchall()[0])


def set_info_daily(user_id: int, value):
    cursor.execute('DELETE FROM daily WHERE user_id=' + str(user_id))
    cursor.execute('INSERT INTO daily (user_id, user_water, user_sleeptime, user_kk, days) VALUES (?, ?, ?, ?, ?)',
                   tuple([user_id] + value))
    conn.commit()


def set_info_history(user_id: int, value):
    cursor.execute('DELETE FROM history WHERE user_id=' + str(user_id))
    cursor.execute('INSERT INTO history (user_id, user_water, user_sleeptime, user_kk, days) VALUES (?, ?, ?, ?, ?)',
                   tuple([user_id] + value))
    conn.commit()


def set_info_test(user_id: int, value):
    cursor.execute('DELETE FROM test WHERE user_id=' + str(user_id))
    cursor.execute('INSERT INTO test (user_id, user_water, user_sleeptime, userkk) VALUES (?, ?, ?, ?)',
                   tuple([user_id] + value))
    conn.commit()


def add_info_daily(user_id: int, value):
    was = get_info(user_id, "daily")
    for i in range(len(value)):
        was[i + 2] += value[i]
    set_info_daily(user_id, was[len(was) - 4 : ])


def add_info_history(user_id: int, value):
    was = get_info(user_id, "history")
    for i in range(len(value)):
        was[i + 2] += value[i]
    set_info_history(user_id, was[len(was) - 4 : ])


def db_table_val(user_id: int, user_water: float, user_sleeptime: float, userkk: float):
    set_info_test(user_id, [user_water, user_sleeptime, userkk])


# id, water_n, sleep_n, kk_n


@bot.message_handler(commands=['start'])
def process_start(message):
    bot.send_message(message.chat.id,
                     text=f"Привет, {message.from_user.first_name}, я бот, который поможет тебе вести здоровый образ жизни. Давай познакомимся.")
    bot.send_message(message.chat.id,
                     text=f"Отправь команду /calculation я и посчитаю норму ккал, воды и сна для тебя")
    user_id = message.from_user.id
    set_info_history(user_id, [0, 0, 0, 0])
    set_info_daily(user_id, [0, 0, 0, 1])


@bot.message_handler(commands=['help'])
def process_help(message):
    bot.send_message(message.chat.id,
                     text=f"Отправь команду /calculation я и посчитаю норму ккал, воды и сна для тебя\n\n"
                          "Отправь команду /start и я очищу данные\n\n"
                          "Отправь команду /water и я добавлю выпитую воду\n\n"
                          "Отправь команду /sleep и я добавлю часы сна\n\n"
                          "Отправь команду /food и я добавлю калории\n\n"
                          "Отправь команду /today и я напишу статистистику за сегодня\n\n"
                          "Отправь команду /summarize и я подведу итоги дня и начну собирать статистику для следующего\n\n"
                          "Отправь команду /history и я пришлю статистику за все прошедшие дни в среднем")


@bot.message_handler(commands=['water'])
def process_water(message):
    global kostil
    bot.send_message(message.chat.id,
                     text=f"введите количество выпитой жидкости в миллилитрах")
    kostil = 5



@bot.message_handler(commands=['sleep'])
def process_sleep(message):
    global kostil
    bot.send_message(message.chat.id,
                     text=f"введите, сколько ч вы проспали")
    kostil = 6


@bot.message_handler(commands=['food'])
def process_food(message):
    global kostil
    bot.send_message(message.chat.id,
                     text=f"введите, сколько ккал вы употребили")
    kostil = 7


@bot.message_handler(commands=['today'])
def process_today(message):
    us_id = message.from_user.id
    res = get_info(us_id, "daily")
    bot.send_message(message.chat.id,
                     text=f"за сегодня вы выпили {res[-4]} мл воды, поспали {res[-3]} ч и употребили {res[-2]} ккал")


@bot.message_handler(commands=['summarize'])
def process_summarize(message):
    us_id = message.from_user.id
    res = get_info(us_id, "daily")
    
    bot.send_message(message.chat.id,
                     text=f"за сегодня вы выпили {res[-4]} мл воды, поспали {res[-3]} ч и употребили {res[-2]} ккал")
    add_info_history(us_id, res[len(res) - 4 : ])
    bot.send_message(message.chat.id, "начался новый день")
    set_info_daily(us_id, [0, 0, 0, 1])


@bot.message_handler(commands=['history'])
def process_history(message):
    us_id = message.from_user.id
    res = get_info(us_id, "history")
    if res[-1] == 0:
        bot.send_message(message.chat.id, "пока что не завершилось ни дня")
        return
    bot.send_message(message.chat.id,
                     text=f"в среднем вы пили {res[-4] / res[-1]} мл воды, спали {res[-3] / res[-1]} ч и употребляли {res[-2] / res[-1]} ккал")
    res = get_info(us_id, "test")
    bot.send_message(message.chat.id,
                     f"А твоя норма составляет {res[-3]} мл,  {res[-2]} ч сна и {res[-1]} ккал в день")




@bot.message_handler(commands=['calculation'])
def process_calculation(message):
    markup = create_inline_keyboard({"male": "male", "female": "female"}, 2)
    bot.send_message(message.chat.id, text=f"{message.from_user.first_name}, выбери свой пол.",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda q: q.data == "male")
def male(q):
    global kostil
    global k_water
    global sleeptime
    global k_kkal
    k_water = 35
    sleeptime = 7
    k_kkal = 5
    bot.delete_message(q.message.chat.id, q.message.message_id)
    bot.send_message(q.message.chat.id, "Твой пол мужской")
    bot.send_message(q.message.chat.id, "Теперь введи, пожалуйста, свой возраст")
    kostil = 1


@bot.callback_query_handler(func=lambda q: q.data == "female")
def female(q):
    global kostil
    global k_water
    global sleeptime
    global k_kkal
    k_water = 32
    sleeptime = 8
    k_kkal = -161
    bot.delete_message(q.message.chat.id, q.message.message_id)
    bot.send_message(q.message.chat.id, "Твой пол женский")
    bot.send_message(q.message.chat.id, "Теперь введи, пожалуйста, свой возраст")
    kostil = 1


@bot.message_handler(content_types=["text"])
def age(message):
    global kostil
    global real_age
    global weight
    if not (message.text.isnumeric()) and (kostil == 1 or kostil == 2):
        bot.send_message(message.chat.id, "Пожалуйста, введите натуральное число")
    elif kostil == 1:
        real_age = int(message.text)
        kostil += 1
        bot.send_message(message.chat.id, "Теперь введи, пожалуйста, свой вес")
    elif kostil == 2:
        kostil = 3
        weight = int(message.text)
        lifestyle = create_inline_keyboard({"active": "active", "normal": "normal", "passive": "passive"}, 3)
        bot.send_message(message.chat.id, f"Остался последний этап. Пожалуйста, охарактеризуй свой образ жизни",
                         reply_markup=lifestyle)
    elif kostil == 5:
        try:
            x = float(message.text)
        except ValueError:
            bot.send_message(message.chat.id, "Пожалуйста, введите число")
            return
        us_id = message.from_user.id
        add_info_daily(us_id, [x, 0, 0, 0])
        bot.send_message(message.chat.id, f"К статистике за день добавилось {x} мл воды")
    elif kostil == 6:
        try:
            x = float(message.text)
        except ValueError:
            bot.send_message(message.chat.id, "Пожалуйста, введите число")
            return
        us_id = message.from_user.id
        add_info_daily(us_id, [0, x, 0, 0])
        bot.send_message(message.chat.id, f"К статистике за день добавилось {x} ч сна")
    elif kostil == 7:
        try:
            x = float(message.text)
        except ValueError:
            bot.send_message(message.chat.id, "Пожалуйста, введите число")
            return
        us_id = message.from_user.id
        add_info_daily(us_id, [0, 0, x, 0])
        bot.send_message(message.chat.id, f"К статистике за день добавилось {x} ккал")
    else:
        bot.send_message(message.chat.id, f"Нажмите команду /help и я вам помогу")


@bot.callback_query_handler(func=lambda q: q.data == "active")
def active(q):
    k_sleeptime = 1
    k_lifestyle = 1.5
    us_id = q.from_user.id
    w_n = k_water * weight * k_lifestyle
    s_n = sleeptime + k_sleeptime
    k_n = (10 * weight + 1065 - 4 * real_age + k_kkal) * k_lifestyle
    bot.delete_message(q.message.chat.id, q.message.message_id)
    bot.send_message(q.message.chat.id, "Ты определил свой образ жизни как активный")
    bot.send_message(q.message.chat.id,
                     f"Отлично, тебе нужно пить {w_n} мл в день, спать {s_n} ч и употреблять {k_n} ккал в день")
    bot.send_message(q.message.chat.id,
                     "Теперь ты можешь начать следить за этими характеристиками, а я буду в этом тебе помогать!")
    db_table_val(user_id=us_id, user_water=w_n, user_sleeptime=s_n, userkk=k_n)


@bot.callback_query_handler(func=lambda q: q.data == "normal")
def normal(q):
    k_sleeptime = 0.5
    k_lifestyle = 1.2
    us_id = q.from_user.id
    w_n = k_water * weight * k_lifestyle
    s_n = sleeptime + k_sleeptime
    k_n = (10 * weight + 1065 - 4 * real_age + k_kkal) * k_lifestyle
    bot.delete_message(q.message.chat.id, q.message.message_id)
    bot.send_message(q.message.chat.id, "Ты определил свой образ жизни как нормальный")
    bot.send_message(q.message.chat.id,
                     f"Отлично, тебе нужно пить {w_n} мл в день, спать {s_n} ч и употреблять {k_n} ккал в день")
    bot.send_message(q.message.chat.id,
                     "Теперь ты можешь начать следить за этими характеристиками, а я буду в этом тебе помогать!")
    db_table_val(user_id=us_id, user_water=w_n, user_sleeptime=s_n, userkk=k_n)


@bot.callback_query_handler(func=lambda q: q.data == "passive")
def passive(q):
    k_sleeptime = 0
    k_lifestyle = 1.0
    us_id = q.from_user.id
    w_n = k_water * weight * k_lifestyle
    s_n = sleeptime + k_sleeptime
    k_n = (10 * weight + 1065 - 4 * real_age + k_kkal) * k_lifestyle
    bot.delete_message(q.message.chat.id, q.message.message_id)
    bot.send_message(q.message.chat.id, "Ты определил свой образ жизни как пассивный")
    bot.send_message(q.message.chat.id,
                     f"Отлично, тебе нужно пить {w_n} мл в день, спать {s_n} ч и употреблять {k_n} ккал в день")
    bot.send_message(q.message.chat.id,
                     "Теперь ты можешь начать следить за этими характеристиками, а я буду в этом тебе помогать!")
    db_table_val(user_id=us_id, user_water=w_n, user_sleeptime=s_n, userkk=k_n)


# def repeat_all_messages(message): # Название функции не играет никакой роли
#     print(message.text)
#     bot.send_message(message.chat.id, message.text)
# def hello_and_calculations(message):
#     if message.text=="привет" :
#         bot.send_message(message.chat.id, "текст разъясняющий что это за бот")
# def start(message):
#     bot.send_message(message.chat.id, "Если ты здесь впервые, напиши привет")


bot.polling()
