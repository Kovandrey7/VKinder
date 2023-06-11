import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import group_token, user_token
from requests_vk import VKapi
from database import *
from button import start_button, search_button, start_over_button, greetings_button, like_button, next_button



class VKBot:
    def __init__(self, group_token, user_token):
        self.vk_group = vk_api.VkApi(token=group_token)
        self.longpoll = VkLongPoll(self.vk_group)
        self.vkapi = VKapi(user_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0
        self.start_dialog = True
        self.start_button = start_button()
        self.search_button = search_button()
        self.start_over_button = start_over_button()
        self.greetings_button = greetings_button()
        self.like_button = like_button()
        self.next_button = next_button()
        self.like = False


    def write_msg(self, user_id, message, attachment=None, keyboard=None):
        param = {'user_id': user_id,
                 'message': message,
                 'attachment': attachment,
                 'random_id': get_random_id(),
                 'keyboard': keyboard.get_keyboard() if keyboard is not None else None
                 }
        self.vk_group.method('messages.send', param)


    def get_photo_string(self, worksheet):
        photos = self.vkapi.get_users_photo(worksheet["id"])
        photo_string = ""
        for photo in photos:
            photo_string += f"photo{photo['owner_id']}_{photo['id']},"

        return photo_string


    def get_photo_string_for_likes(self, worksheet):
        photos = self.vkapi.get_users_photo(worksheet)
        photo_string = ""
        for photo in photos:
            photo_string += f"photo{photo['owner_id']}_{photo['id']},"

        return photo_string


    def check_worksheet(self, event):
        worksheet = self.worksheets.pop()
        while check_user(engine, event.user_id, worksheet["id"]):
            if self.worksheets:
                worksheet = self.worksheets.pop()
            else:
                self.offset += 50
                self.worksheets = self.vkapi.search_worksheet(self.params, self.offset)
                worksheet = self.worksheets.pop()
        return worksheet


    def event_handler(self):
        check_and_create_database(db_url_object)
        Base.metadata.create_all(engine)

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text.lower()
                user_id = event.user_id

                if self.start_dialog and (request == "привет" or request == "начать сначала!"):
                    self.params = self.vkapi.get_user_info(event.user_id)
                    keyboard = self.start_button
                    self.write_msg(user_id=user_id,
                                   message=f"Привет, {self.params['name']}!\n "
                                           f"Выбери нужное действие!",
                                   keyboard=keyboard
                                   )
                    self.start_dialog = False

                elif self.start_dialog is False and request == "начать работу бота":
                    if self.params["city"]:
                        keyboard = self.search_button
                        self.write_msg(user_id=user_id,
                                       message="Выбери нужное действие!",
                                       keyboard=keyboard
                                       )
                    else:
                        self.write_msg(user_id=user_id,
                                       message="Для корректной работы напиши название своего города."
                                       )
                        for event in self.longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                city = event.text.title()
                                self.params["city"] = city
                                keyboard = self.search_button
                                self.write_msg(user_id=user_id,
                                               message="Отлично! Выбери нужное действие!",
                                               keyboard=keyboard
                                               )
                                break
                    self.start_dialog = False

                elif self.start_dialog is False and (request == "поиск новых анкет" or request == "продолжить поиск"):
                    self.write_msg(user_id=user_id,
                                   message="Начинаю поиск анкет"
                                   )

                    if self.worksheets:
                        worksheet = self.check_worksheet(event)
                        attachment = self.get_photo_string(worksheet)
                    else:
                        self.worksheets = self.vkapi.search_worksheet(self.params, self.offset)
                        worksheet = self.check_worksheet(event)
                        attachment = self.get_photo_string(worksheet)
                        self.offset += 50

                    self.write_msg(user_id=user_id,
                                   message=f"Имя: {worksheet['name']}, ссылка VK: vk.com/id{worksheet['id']}",
                                   attachment=attachment
                                   )
                    keyboard = self.like_button
                    self.write_msg(user_id=user_id,
                                   message="Добавить анкету в избранное?",
                                   keyboard=keyboard
                                   )
                    for event in self.longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            request = event.text.lower()

                            if request == "добавить анкету в избранное":
                                self.like = True
                                add_user(engine, event.user_id, worksheet["id"], like=self.like)
                                self.write_msg(user_id=user_id,
                                               message="Анкета добавлена в избранное"
                                               )
                                break
                            elif request == "пропустить":
                                add_user(engine, event.user_id, worksheet["id"])
                                break
                            else:
                                self.write_msg(user_id=user_id,
                                               message=f"Не понимаю команду, воспользуйтесь кнопками."
                                               )
                    keyboard = self.search_button
                    self.write_msg(user_id=user_id,
                                   message="Продолжить поиск?",
                                   keyboard=keyboard)
                    self.start_dialog = False

                elif self.start_dialog is False and request == "показать избранные анкеты":
                    likes_list = get_likes_list(event.user_id)
                    if likes_list:
                        worksheet_id = likes_list.pop()
                        attachment = self.get_photo_string_for_likes(worksheet_id)
                        self.write_msg(user_id=user_id,
                                       message=f"Cсылка VK: vk.com/id{worksheet_id}",
                                       attachment=attachment
                                       )
                        keyboard = self.next_button
                        self.write_msg(user_id=user_id,
                                       message="Выбери нужное действие!",
                                       keyboard=keyboard
                                       )
                        for event in self.longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                request = event.text.lower()

                                if request == "следующая избранная анкета":
                                    if likes_list:
                                        worksheet_id = likes_list.pop()
                                        attachment = self.get_photo_string_for_likes(worksheet_id)
                                        self.write_msg(user_id=user_id,
                                                       message=f"Cсылка VK: vk.com/id{worksheet_id}",
                                                       attachment=attachment, keyboard=keyboard
                                                       )
                                    else:
                                        keyboard = self.search_button
                                        self.write_msg(user_id=user_id,
                                                       message=f"Избранные анкеты анкеты закончились.\n"
                                                               f"Начать поиск новых анкет?",
                                                       keyboard=keyboard
                                                       )
                                        break


                                elif request == "закончить просмотр избранных анкет":
                                    keyboard = self.search_button
                                    self.write_msg(user_id=user_id,
                                                    message="Выбери нужное действие!",
                                                    keyboard=keyboard
                                                   )
                                    break

                                else:
                                    self.write_msg(user_id=user_id,
                                                   message=f"Не понимаю команду, воспользуйтесь кнопками."
                                                   )

                    else:
                        keyboard = self.search_button
                        self.write_msg(user_id=user_id,
                                       message="Отстутствуют избранные анкеты, для продолжения выбери нужное действие!",
                                       keyboard=keyboard
                                       )


                elif request == "завершить":
                    keyboard = self.start_over_button
                    self.write_msg(user_id=user_id,
                                   message="До новых встреч!",
                                   keyboard=keyboard
                                   )
                    self.start_dialog = True
                    keyboard = self.greetings_button
                    self.write_msg(user_id=user_id,
                                   message="Нажмите кнопку 'Привет' для начала работы",
                                   keyboard=keyboard
                                   )

                else:
                    if self.start_dialog:
                        keyboard = self.start_over_button
                        self.write_msg(user_id=user_id,
                                       message="Не понимаю команду, воспользуйтесь кнопками.",
                                       keyboard=keyboard
                                       )
                    else:
                        self.write_msg(user_id=user_id,
                                       message="Не понимаю команду, воспользуйтесь кнопками."
                                       )


if __name__ == "__main__":
    VKBot = VKBot(group_token, user_token)
    VKBot.event_handler()

