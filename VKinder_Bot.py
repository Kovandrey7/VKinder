import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import group_token, user_token
from requests_vk import VKapi


class VKBot():
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


    def event_handler(self):

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text.lower()
                user_id = event.user_id

                if request == "привет":
                    self.params = self.vkapi.get_user_info(event.user_id)
                    self.write_msg(user_id=user_id, message=f"Привет, {self.params['name']}!")

                elif request == "поиск":
                    self.write_msg(user_id=user_id, message="Начинаю поиск анкет")

                    if self.worksheets:
                        worksheet = self.worksheets.pop()
                        photos = self.vkapi.get_users_photo(worksheet["id"])
                        photo_string = ""
                        for photo in photos:
                            photo_string += f"photo{photo['owner_id']}_{photo['id']}"

                    else:
                        self.worksheets = self.vkapi.search_worksheet(self.params, self.offset)
                        worksheet = self.worksheets.pop()
                        photos = self.vkapi.get_users_photo(worksheet["id"])
                        photo_string = ""
                        for photo in photos:
                            photo_string += f"photo{photo['owner_id']}_{photo['id']}"
                        self.offset += 50

                    self.write_msg(user_id=user_id,
                                   message=f"Имя: {worksheet['name']}, ссылка VK: vk.com/id{worksheet['id']}",
                                   attachment=photo_string
                                   )

                elif request == "пока":
                    self.write_msg(user_id=user_id, message="Пока((")

                elif request == "проверка":
                    message = str(self.vkapi.get_user_info(event.user_id))
                    self.write_msg(user_id=user_id, message=message)

                else:
                    self.write_msg(user_id=user_id, message="Не поняла вашего ответа...")


if __name__ == "__main__":
    VKBot = VKBot(group_token, user_token)
    VKBot.event_handler()

