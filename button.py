from vk_api.keyboard import VkKeyboard


def start_button():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Начать")
    keyboard.add_button("Завершить")
    return keyboard


def search_button():
    keyboard = VkKeyboard()
    keyboard.add_button("Поиск")
    keyboard.add_button("Завершить")
    return keyboard


def start_over():
    keyboard = VkKeyboard()
    keyboard.add_button("Начать сначала!")
    return keyboard


def greetings():
    keyboard = VkKeyboard()
    keyboard.add_button("Привет")
    return keyboard