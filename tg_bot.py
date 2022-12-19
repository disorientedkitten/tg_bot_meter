import telebot
import sqlite3

conn = sqlite3.connect('/Users/natala/Desktop/Python матфак/tg_watermeter_base.db', check_same_thread=False)
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
k_water = 32
weight = 65
sleeptime = 7.5
real_age = 20
k_kkal = 0
k_lifestile = 0
kostil = 0


# формула рассчета каллорий по харрису бенедикту (10*weight + 1065 - 5*age + k_kkal) * k_lifestile
# формула для рассчета сна
# формула для рассчета воды k_water*weight*k_lifestile

def db_table_val(user_id: int, user_water: float, user_sleeptime: float, userkk: int):
    cursor.execute('INSERT INTO water (id, water_n, sleep_n, kk_n) VALUES (?, ?, ?, ?)',
                   (user_id, user_water, user_sleeptime, userkk))
    conn.commit()


#id, water_n, sleep_n, kk_n


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,
                     text=f"Привет, {message.from_user.first_name}, я бот, который поможет тебе вести здоровый образ жизни. Давай познакомимся.")
    bot.send_message(message.chat.id,
                     text=f"Отправь мне команду /calculation чтобы я посчитал норму каллорий, воды и сна для тебя")

@bot.message_handler(commands=['help'])
def welcome(message):
    bot.send_message(message.chat.id,
                     text=f"Привет, {message.from_user.first_name}, я бот, который поможет тебе вести здоровый образ жизни. Давай познакомимся.")
    bot.send_message(message.chat.id,
                     text=f"Отправь команду /calculation чтобы я посчитал норму каллорий, воды и сна для тебя"
                          "Отправь команду /water и я добавлю выпитую воду"
                          "Отправь команду /sleep и я добавлю часы сна"
                          "Отправь команду /food и я добавлю калории"
                          "Отправь мне команду /today и я напишу статистистику за сегодня")



@bot.message_handler(commands=['water'])
def welcome(message):
    bot.send_message(message.chat.id,
                    text = f"водичка")

@bot.message_handler(commands=['sleep'])
def welcome(message):
    bot.send_message(message.chat.id,
                     text=f"сон")

@bot.message_handler(commands=['food'])
def welcome(message):
    bot.send_message(message.chat.id,
                     text=f"покушанье")

# тут было это reply_markup=markup хз зач


@bot.message_handler(commands=['calculation'])
def welcome(message):
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
        lifestile = create_inline_keyboard({"active": "active", "normal": "normal", "passive": "passive"}, 3)
        bot.send_message(message.chat.id, f"Остался последний этап. Пожалуйста, охарактеризуй свой образ жизни",
                         reply_markup=lifestile)
    else:
        bot.send_message(message.chat.id, f"Нажмите команду /help и я вам помогу")


@bot.callback_query_handler(func=lambda q: q.data == "active")
def active(q):
    k_sleeptime = 1
    k_lifestile = 1.5
    us_id = q.from_user.id
    w_n = k_water * weight * k_lifestile
    s_n = sleeptime + k_sleeptime
    k_n = (10 * weight + 1065 - 4 * real_age + k_kkal) * k_lifestile
    bot.delete_message(q.message.chat.id, q.message.message_id)
    bot.send_message(q.message.chat.id, "Ты определил свой образ жизни как активный")
    bot.send_message(q.message.chat.id,
                     f"Отлично, тебе нужно пить {w_n} миллилитров в день, спать {s_n} часов и употреблять {k_n} каллорий в день")
    bot.send_message(q.message.chat.id,
                     "Теперь ты можешь начать следить за этими характеристиками, а я буду в этом тебе помогать!")
    #db_table_val(user_id=us_id, user_water=w_n, user_sleeptime=s_n, userkk=k_n)


@bot.callback_query_handler(func=lambda q: q.data == "normal")
def normal(q):
    k_sleeptime = 0.5
    k_lifestile = 1.2
    us_id = q.from_user.id
    w_n = k_water * weight * k_lifestile
    s_n = sleeptime + k_sleeptime
    k_n = (10 * weight + 1065 - 4 * real_age + k_kkal) * k_lifestile
    bot.delete_message(q.message.chat.id, q.message.message_id)
    bot.send_message(q.message.chat.id, "Ты определил свой образ жизни как нормальный")
    bot.send_message(q.message.chat.id,
                     f"Отлично, тебе нужно пить {w_n} миллилитров в день, спать {s_n} часов и употреблять {k_n} каллорий в день")
    bot.send_message(q.message.chat.id,
                     "Теперь ты можешь начать следить за этими характеристиками, а я буду в этом тебе помогать!")
    #db_table_val(user_id=us_id, user_water=w_n, user_sleeptime=s_n, userkk=k_n)


@bot.callback_query_handler(func=lambda q: q.data == "passive")
def passive(q):
    k_sleeptime = 0
    k_lifestile = 1.0
    us_id = q.from_user.id
    w_n = k_water * weight * k_lifestile
    s_n = sleeptime + k_sleeptime
    k_n = (10 * weight + 1065 - 4 * real_age + k_kkal) * k_lifestile
    bot.delete_message(q.message.chat.id, q.message.message_id)
    bot.send_message(q.message.chat.id, "Ты определил свой образ жизни как пассивный")
    bot.send_message(q.message.chat.id,
                     f"Отлично, тебе нужно пить {w_n} миллилитров в день, спать {s_n} часов и употреблять {k_n} каллорий в день")
    bot.send_message(q.message.chat.id,
                     "Теперь ты можешь начать следить за этими характеристиками, а я буду в этом тебе помогать!")
    #db_table_val(user_id=us_id, user_water=w_n, user_sleeptime=s_n, userkk=k_n)




# def repeat_all_messages(message): # Название функции не играет никакой роли
#     print(message.text)
#     bot.send_message(message.chat.id, message.text)
# def hello_and_calculations(message):
#     if message.text=="привет" :
#         bot.send_message(message.chat.id, "текст разъясняющий что это за бот")
# def start(message):
#     bot.send_message(message.chat.id, "Если ты здесь впервые, напиши привет")


bot.polling()
