import vk_api
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import json
import random
from config import VK_TOKEN


vk_session = vk_api.VkApi(token=VK_TOKEN)
longpoll = VkBotLongPoll(vk_session, group_id=208511320)

with open('vk-pepega-bot/bot_config.json', encoding='utf-8') as f:
    bot_config = json.load(f)

# Функция отправления сообщений в чат
def sender(id, text):
    vk_session.method('messages.send', {'chat_id' : id, 'message' : text, 'random_id' : get_random_id()})

# Сравнения полученного от пользователя сообщения с примерами в json файле
# При совпадении - возврат рандомного ответа из соответсвующего намерения, иначе - возрат фразы провала
def get_message(message):
    for intent, intent_data in bot_config['intents'].items():   
        if message in intent_data['examples']:
            return random.choice(intent_data['responses'])
    else:       
        return random.choice(bot_config['failure_phrases'])

# Прослушивание чата в бесконечном цикле, в ожидании команды активации
# После активации, управление передается в функцию main, после чего цикл завершается
def start_bot():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat and event.message.get('text') !='':      
            id = event.chat_id  
            bot_response = event.message.get('text').lower()
            if bot_response == 'bot':
                sender(id, '(╮°-°)╮┳━━┳')
                main()  
                break     

# Обработка сообщений пользователей и отправда ответов в чат
# Ожидание команды дезактивации, после которой управление переходит в функцию start_bot
def main():
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

if __name__ == '__main__':
    start_bot()      

