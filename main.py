import vk_api
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import json
import random
import schedule
import time
import requests
from threading import *
from config import VK_TOKEN, WEATHER_TOKEN
from news_parser import News


vk_session = vk_api.VkApi(token=VK_TOKEN)
longpoll = VkBotLongPoll(vk_session, group_id=208511320)


with open('vk-group-chat-bot/bot_config.json', encoding='utf-8') as f:
    bot_config = json.load(f)

# Функция отправления сообщений в чат
def sender(id, text):
    msg_id = abs(get_random_id())
    # Ответом на данный метод должно возвращаться id сообщения, он же его обнуляет -_-
    vk_session.method('messages.send', {'peer_id' : (2000000000 + id), 'message' : text, 'random_id' : msg_id})
    return msg_id 
    
# Обработчик для читабельного вывода погоды
def tuner(temp):
    for key, value in temp.items():
        int_value = round(value)
        if int_value > 0:
            temp[key] = '+' + str(int_value)
        elif value == 0:
            temp[key] = ' ' + str(int_value)
        else:
            temp[key] = str(int_value)            
    return temp

# Запрос погоды через API, парсинг ответа и отправка данных в чат
# !!!Перенос строки невозможнен по причине смещения текста на мобильных устройствах!!!
def send_weather():
    weather_pack = (requests.get(f'https://api.openweathermap.org/data/2.5/onecall?lat=53&lon=50&units=metric&lang=ru&exclude=current,minutely,hourly&appid={WEATHER_TOKEN}')).json()
    weather = weather_pack['daily'][0]
    indent = '&#12288;'
    alerts = ''
    temp = tuner(weather['temp'])
    feels_temp = tuner(weather['feels_like'])
    for alert in weather_pack['alerts']:
        if alert['description'] != '':
            alerts += alert['description'] + '&#10071; '  
    sender(2, 'Доброе утро!')                
    msg_id = sender(2, f"Утро{indent}День{indent}Вечер{indent}Ночь\n{indent}\n{temp['morn']}{indent}{indent}{indent}{temp['day']}{indent}{indent}{indent}{temp['eve']}{indent}{indent}{indent}{temp['night']}\n{indent}\n{feels_temp['morn']}{indent}{indent}{indent}{feels_temp['day']}{indent}{indent}{indent}{feels_temp['eve']}{indent}{indent}{indent}{feels_temp['night']}\n{indent}\nВетер: {round(weather['wind_speed'], 1)}м/с{indent}Порывы: {round(weather['wind_gust'], 1)}м/с\n{(weather['weather'][0]['description']).capitalize()}\n{alerts}")
    return msg_id

# Создание расписания отправки погоды
def create_schedule():
    schedule.every().day.at('06:00').do(send_weather)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Сравнения полученного от пользователя сообщения с примерами в json файле
# При совпадении - возврат рандомного ответа из соответсвующего намерения, иначе - возрат фразы провала
def get_message(message):
    for intent, intent_data in bot_config['intents'].items():   
        if message in intent_data['examples']:
            return random.choice(intent_data['responses'])
    else:       
        return random.choice(bot_config['failure_phrases'])

# Прослушивание чата в бесконечном цикле, в ожидании команды активации
# После активации, управление передается в функцию bot, после чего цикл завершается
def start_bot():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat and event.message.get('text') !='':      
            id = event.chat_id
            bot_response = event.message.get('text').lower()
            if bot_response == 'weather':
                msg_id = send_weather()
                # Неработающая хренатень
                #vk_session.method('messages.pin', {'peer_id' : 2000000002, 'message_id' : msg_id})   
            elif bot_response == 'news':
                sender(id, News().post)
            elif bot_response == 'bot':
                sender(id, '(╮°-°)╮┳━━┳')
                bot()  
                break     

# Обработка сообщений пользователей и отправда ответов в чат
# Ожидание команды дезактивации, после которой управление переходит в функцию start_bot
def bot():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat and event.message.get('text') !='':      
            id = event.chat_id
            msg = event.message.get('text').lower()
            if msg != 'bb':
                bot_response = get_message(msg)
                sender(id, bot_response)
            else:
                sender(id, '(╯°□°)╯ ┻━━┻')
                start_bot()
                break

def main():
    thread_one = Thread(target=create_schedule)
    thread_one.start()
    start_bot()    
    thread_one.join()      

if __name__ == '__main__':
    main()    

