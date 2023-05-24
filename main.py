from requests_vk import write_msg
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

with open("config.txt", "r") as file_object:
    token_group = file_object.readline().strip()

token = token_group

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text.lower()

            if request == "привет":
                write_msg(event.user_id, f"Хай, {event.user_id}")
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")