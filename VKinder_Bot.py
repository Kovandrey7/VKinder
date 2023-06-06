import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import group_token, user_token
from requests_vk import VKapi
from database import *



class VKBot:
    def __init__(self, group_token, user_token):
        self.vk_group = vk_api.VkApi(token=group_token)
        self.longpoll = VkLongPoll(self.vk_group)
        self.vkapi = VKapi(user_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0


    def write_msg(self, user_id, message, attachment=None):
        self.vk_group.method('messages.send',
                        {
                            'user_id': user_id,
                            'message': message,
                            'attachment': attachment,
                            'random_id': get_random_id()
                        }
                        )


    def get_photo_string(self, worksheet):
        photos = self.vkapi.get_users_photo(worksheet["id"])
        photo_string = ""
        for photo in photos:
            photo_string += f"photo{photo['owner_id']}_{photo['id']},"

        return photo_string

    def event_handler(self):
        check_and_create_database(db_url_object)
        Base.metadata.create_all(engine)

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text.lower()
                user_id = event.user_id

                if request == "привет":
                    self.params = self.vkapi.get_user_info(event.user_id)
                    if self.params["city"]:
                        self.write_msg(user_id=user_id, message=f"Привет, {self.params['name']}!")
                    else:
                        self.write_msg(user_id=user_id, message=f"Привет, {self.params['name']}!")
                        self.write_msg(user_id=user_id,
                                       message="Для корректной работы введите название вашего города:")
                        for event in self.longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                city = event.text.title()
                                self.params["city"] = city
                                self.write_msg(user_id=user_id,
                                               message="Отлично! Напишите в чате 'поиск' для подбора анкет: ")
                                break

                elif request == "поиск":
                    self.write_msg(user_id=user_id, message="Начинаю поиск анкет")

                    if self.worksheets:
                        worksheet = self.worksheets.pop()
                        attachment = self.get_photo_string(worksheet)
                    else:
                        self.worksheets = self.vkapi.search_worksheet(self.params, self.offset)
                        worksheet = self.worksheets.pop()
                        while check_user(engine, event.user_id, worksheet["id"]):
                            if self.worksheets:
                                worksheet = self.worksheets.pop()
                            else:
                                self.offset += 50
                                self.worksheets = self.vkapi.search_worksheet(self.params, self.offset)
                                worksheet = self.worksheets.pop()
                        attachment = self.get_photo_string(worksheet)
                        self.offset += 50

                    self.write_msg(user_id=user_id,
                                   message=f"Имя: {worksheet['name']}, ссылка VK: vk.com/id{worksheet['id']}",
                                   attachment=attachment
                                   )

                    add_user(engine, event.user_id, worksheet["id"])

                elif request == "пока":
                    self.write_msg(user_id=user_id, message="Пока((")

                else:
                    self.write_msg(user_id=user_id, message="Не поняла вашего сообщения...")


if __name__ == "__main__":
    VKBot = VKBot(group_token, user_token)
    VKBot.event_handler()

