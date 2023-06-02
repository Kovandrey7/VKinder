import vk_api
from config import user_token
from pprint import pprint
from vk_api.exceptions import ApiError
from datetime import datetime


class VKapi:
    def __init__(self, token):
        self.vkapi = vk_api.VkApi(token=token)


    def bdate_to_yaer(self, bdate):
        user_year = bdate.split(".")[-1]
        year_now = datetime.now().year
        result = year_now - int(user_year)
        return result


    def get_user_info(self, user_id):
        try:
            resp, = self.vkapi.method("users.get",
                                      {
                                          "user_ids": user_id,
                                          "fields": "bdate, city, sex"
                                      }
                                      )

        except ApiError as error:
            resp = {}
            print(f"Error = {error}")

        result = {
                    "name": resp["first_name"] + " " + resp["last_name"]
                    if "last_name" in resp and "last_name" in resp else None,
                    "sex": resp.get("sex"),
                    "city": resp.get("city")["title"] if resp.get("city") is not None else None,
                    "year": self.bdate_to_yaer(resp.get("bdate"))
        }

        return result


    def search_worksheet(self, params, offset):
        try:
            users = self.vkapi.method("users.search",
                                      {
                                          "count": 50,
                                          "offset": offset,
                                          "hometown": params["city"],
                                          "sex": 1 if params["sex"] == 2 else 2,
                                          "has_photo": 1,
                                          "age_from": params["year"] - 3,
                                          "age_to": params["year"] + 3
                                      }
                                      )

        except ApiError as error:
            users = []
            print(f"Error = {error}")

        result = [
            {
                "name": item["first_name"] + " " + item["last_name"],
                "id": item["id"]
            } for item in users['items'] if item["is_closed"] is False
        ]

        return result


    def get_users_photo(self, id):
        try:
            photos = self.vkapi.method("photos.get",
                                      {
                                          "owner_id": id,
                                          "album_id": "profile",
                                          "extended": 1
                                      }
                                      )

        except ApiError as error:
            photos = {}
            print(f"Error = {error}")

        result = [
            {
                "owner_id": item["owner_id"],
                "id": item["id"],
                "likes": item["likes"]["count"],
                "comments": item["comments"]["count"]
            } for item in photos["items"]
        ]

        return result[0:2]


if __name__ == "__main__":
    user_id = 4417214
    vkapi = VKapi(user_token)
    params = vkapi.get_user_info(user_id)
    worksheets = vkapi.search_worksheet(params, 0)
    worksheet = worksheets.pop()
    photos = vkapi.get_users_photo(worksheet["id"])

    pprint(params)
    print(worksheets)
    print(worksheet)
    print(photos)
