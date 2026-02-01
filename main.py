import random, json
from datetime import datetime, timezone

from config import VKADMIN_ID, VKTOKEN, TGCHAT, TGTOKEN #config.py

#import for telegram
import telebot;
tgbot = telebot.TeleBot(TGTOKEN)

#import for vk
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from vkbot import VkBot

def write_msg(user_id, message, key):
    vk.method('messages.send',
              {'user_id': user_id,
               'message': message,
               'keyboard': key,
               'random_id': random.randint(0, 2048)})

vk = vk_api.VkApi(token=VKTOKEN)
longpoll = VkLongPoll(vk)

main_keyboard = {
    "one_time": False,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "payload": "{\"button\": \"1\"}",
                "label": "Отправить"
            },
            "color": "positive"
        }]
    ]
}
main_keyboard = json.dumps(main_keyboard, ensure_ascii=False).encode('utf-8')
main_keyboard = str(main_keyboard.decode('utf-8'))

cancel_keyboard = {
    "one_time": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "payload": "{\"button\": \"1\"}",
                "label": "Отмена"
            },
            "color": "negative"
        }]
    ]
}
cancel_keyboard = json.dumps(cancel_keyboard, ensure_ascii=False).encode('utf-8')
cancel_keyboard = str(cancel_keyboard.decode('utf-8'))


try:
    print("started")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                vkbot = VkBot(event.user_id)
                
                if event.user_id == VKADMIN_ID:
                    if event.text.lower() == "отправить":
                        # write_msg(event.user_id, f"{event.text}", 0)
                        write_msg(event.user_id, "Ожидаю текст", cancel_keyboard)
                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW:
                                if event.to_me:
                                    if event.text.lower() == "отмена":
                                        write_msg(event.user_id, "Отмена пересылки", main_keyboard)
                                        break
                                    current_time_utc = datetime.now(timezone.utc)
                                    formatted_time = current_time_utc.strftime('%d.%m.%Y %H:%M:%S UTC+0')
                                    debug_text = f"--------\n[{formatted_time}] FORWARDED FROM {event.user_id}:\n{event.text}\n--------\n\n"

                                    #output forwarded text
                                    tgbot.send_message(TGCHAT, event.text)
                                    write_msg(event.user_id, "Отправлено!", main_keyboard)
                                    print(debug_text)

                                    break


                    # elif event.text.lower() == "test":
                    #     write_msg(event.user_id, f"{event.user_id}", 0)

                    else:
                        write_msg(event.user_id, f"{event.text}", main_keyboard)
                
                else:
                    write_msg(event.user_id, "У вас нет доступа к этому боту", 0)
                    write_msg(VKADMIN_ID, f"Trying [{event.user_id}]: {event.text}", 0) #отправка администратору попытку использования

except Exception as e:
    print(e)
