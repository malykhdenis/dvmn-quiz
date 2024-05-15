import vk_api as vk
from environs import Env
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id


def echo(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )


if __name__ == "__main__":
    env = Env()
    env.read_env()

    vk_session = vk.VkApi(token=env.str('VK_GROUP_TOKEN'))
    vk_api = vk_session.get_api()

    keyboard = VkKeyboard()
    keyboard.add_button('button')

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            echo(event, vk_api)
