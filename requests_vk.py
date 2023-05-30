from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from datetime import datetime
# from pprint import pprint as print


with open("config.txt", "r") as file_object:
    token_group = file_object.readline().strip()
    token_user = file_object.readline().strip()

token = token_group
user_token = token_user
vk = vk_api.VkApi(token=token)
vk_user = vk_api.VkApi(token=token_user)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})


def get_user_info(user_id):
    user_info = {}
    res = vk_user.method("users.get", {
        "users_ids": user_id,
        "fields": "first_name, last_name, bdate, city, sex"
    })
    if res:
        for key, value in res[0].items():
            if key == "city":
                user_info[key] = value["id"]
            else:
                user_info[key] = value
    else:
        write_msg(user_info["id"], "Непредвиденная ошибка")
        return None
    return user_info


def convert_city_name_into_city_id(city_name: str, user_info):
    res = vk_user.method("database.getCities",
                         {"country_ids": 1,
                          "q": city_name,
                          "need_all": 0,
                          "count": 10
                          })
    if res:
        city_id = res.get('items')[0]["id"]
        return city_id
    else:
        write_msg(user_info["id"], 'Ошибка ввода города')
        return None


def get_city_id(user_info):
    if user_info:
        if user_info.get("city"):
            user_city_id = user_info["city"]
            return user_city_id
        else:
            write_msg(user_info["id"], "Введите название вашего города: ")
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        city_id = convert_city_name_into_city_id(event.text, user_info)
                        user_info["city"] = city_id
                        user_city_id = user_info["city"]
                        return user_city_id
    else:
        write_msg(user_info["id"], "Непредвиденная ошибка!")
        return None


def get_sex(user_info):
    if user_info:
        sex = user_info["sex"]
        return sex
    else:
        write_msg(user_info["id"], "Непредвиденная ошибка!")
        return None


def get_bdate_year(user_info):
    if user_info["bdate"]:
        if len(user_info["bdate"].split(".")) == 3:
            bdate_year = user_info["bdate"].split(".")[-1]
            return bdate_year
        else:
            write_msg(user_info["id"], "Введите год вашего рождения в формате 'YYYY': ")
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    user_info["bdate"] = event.text
                    bdate_year = user_info["bdate"]
                    return bdate_year
    else:
        write_msg(user_info["id"], "Непредвиденная ошибка!")
        return None


def users_search(user_info):
    res = vk_user.method("users.search", {
        "age_from": (datetime.now().date().year - int(get_bdate_year(get_user_info(user_info["id"])))) - 3,
        "age_to": (datetime.now().date().year - int(get_bdate_year(get_user_info(user_info["id"])))) + 3,
        "sex": 3 - get_sex(get_user_info(user_info["id"])),
        "status": 6,
        "city": get_city_id(get_user_info(user_info["id"])),
        "count": 5,
        "has_photo": 1,
    })
    return res["items"]

