from random import randrange
import vk_api


with open("config.txt", "r") as file_object:
    token_group = file_object.readline().strip()
    token_user = file_object.readline().strip()

token = token_group
user_token = token_user
vk = vk_api.VkApi(token=token)
vk_user = vk_api.VkApi(token=token_user)

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

    return user_info

print(get_user_info(4417214))

# def user_search(user_data):
#     res = vk.method("user_search", {
#
#     })