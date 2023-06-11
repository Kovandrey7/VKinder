from vk_api.keyboard import VkKeyboard


def start_button():
    keyboard = VkKeyboard()
    keyboard.add_button("Начать работу бота")
    keyboard.add_button("Завершить")
    return keyboard


def search_button():
    keyboard = VkKeyboard()
    keyboard.add_button("Поиск новых анкет")
    keyboard.add_line()
    keyboard.add_button("Показать избранные анкеты")
    keyboard.add_line()
    keyboard.add_button("Завершить")
    return keyboard


def start_over_button():
    keyboard = VkKeyboard()
    keyboard.add_button("Начать сначала!")
    return keyboard


def greetings_button():
    keyboard = VkKeyboard()
    keyboard.add_button("Привет")
    return keyboard


def like_button():
    keyboard = VkKeyboard()
    keyboard.add_button("Добавить анкету в избранное")
    keyboard.add_line()
    keyboard.add_button("Пропустить")
    return keyboard


def next_button():
    keyboard = VkKeyboard()
    keyboard.add_button("Следующая избранная анкета")
    keyboard.add_line()
    keyboard.add_button("Закончить просмотр избранных анкет")
    return keyboard