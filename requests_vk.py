import vk_api
from config import user_token, group_token
from pprint import pprint
from vk_api.exceptions import ApiError
from datetime import datetime


class VKapi:
    def __init__(self, user_token):
        self.vkapi_user = vk_api.VkApi(token=user_token)


    def bdate_to_yaer(self, bdate):
        user_year = bdate.split(".")[-1]
        year_now = datetime.now().year
        result = year_now - int(user_year)
        return result


    def get_user_info(self, user_id):
        try:
            resp, = self.vkapi_user.method("users.get",
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
            users = self.vkapi_user.method("users.search",
                                      {
                                          "count": 50,
                                          "offset": offset,
                                          "hometown": params["city"],
                                          "sex": 1 if params["sex"] == 2 else 2,
                                          "has_photo": 1,
                                          "age_from": params["year"] - 3,
                                          "age_to": params["year"] + 3,
                                          "status": 6
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
            photos = self.vkapi_user.method("photos.get",
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
        result.sort(key=lambda x: x["likes"] + x["comments"], reverse=True)
        return result[0:3]


if __name__ == "__main__":
    user_id = 4417214
    vkapi = VKapi(user_token)
    params = vkapi.get_user_info(user_id)
    worksheets = vkapi.search_worksheet(params, 0)
    worksheet = worksheets.pop()
    photos = vkapi.get_users_photo(worksheet["id"])

    # pprint(params)
    # pprint(worksheets)
    # pprint(worksheet)
    # pprint(photos)
