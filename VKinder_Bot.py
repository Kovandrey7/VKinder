from requests_vk import *
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

with open("config.txt", "r") as file_object:
    token_group = file_object.readline().strip()
    token_user = file_object.readline().strip()

token = token_group
user_token = token_user
vk = vk_api.VkApi(token=token)
vk_user = vk_api.VkApi(token=token_user)
longpoll = VkLongPoll(vk)


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text.lower()

            if request == "привет":
                message = users_search(get_user_info(event.user_id))
                write_msg(user_id=event.user_id, message=message)

            elif request == "пока":
                write_msg(event.user_id, "Пока((")

            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")