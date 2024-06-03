import logging
import random
import vk_api as vk
import redis
from environs import Env
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from get_questions import get_questions


def start(event: vk.longpoll.Event, vk_api: vk.vk_api.VkApiMethod) -> None:
    """Send a message when the command /start is issued."""
    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос')
    vk_api.messages.send(
        user_id=event.user_id,
        message='Для начала нажмите "Новый вопрос"',
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )


def ask_question(
        event: vk.longpoll.Event,
        vk_api: vk.vk_api.VkApiMethod,
        questions: str,
        db: redis.Redis,
) -> None:
    """Ask random question."""
    keyboard = VkKeyboard()
    keyboard.add_button('Сдаться')
    question = random.choice(list(questions))
    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )
    db.set(event.user_id, question)


def give_up(
        event: vk.longpoll.Event,
        vk_api: vk.vk_api.VkApiMethod,
        questions: dict,
        db: redis.Redis,
) -> None:
    """Get answer and another question."""
    correct_answer = questions[
        db.get(event.user_id).decode('utf-8')
    ]['answer']
    vk_api.messages.send(
        user_id=event.user_id,
        message=correct_answer,
        random_id=get_random_id(),
    )
    next_question = random.choice(list(questions))
    db.set(event.user_id, next_question)
    vk_api.messages.send(
        user_id=event.user_id,
        message=next_question,
        random_id=get_random_id(),
    )


def check_answer(
        event: vk.longpoll.Event,
        vk_api: vk.vk_api.VkApiMethod,
        questions: dict,
        db: redis.Redis,
) -> None:
    """Check answer in the user message."""
    correct_answer = questions[
        db.get(event.user_id).decode('utf-8')
    ]
    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос')
    if event.text == correct_answer['short_answer']:
        vk_api.messages.send(
            user_id=event.user_id,
            message='Правильно! Поздравляю!',
            random_id=get_random_id(),
        )
        if correct_answer['comment']:
            vk_api.messages.send(
                user_id=event.user_id,
                message=f'{correct_answer["comment"]}',
                random_id=get_random_id(),
            )
        vk_api.messages.send(
            user_id=event.user_id,
            message='Для следующего вопроса нажми «Новый вопрос».',
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
        )
    else:
        vk_api.messages.send(
            user_id=event.user_id,
            message='Неправильно… Попробуешь ещё раз?'
                    'Для следующего вопроса нажми «Новый вопрос».',
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
        )


def main(token: str) -> None:
    """Start VK bot."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )

    env = Env()
    env.read_env()

    vk_session = vk.VkApi(token=env.str('VK_GROUP_TOKEN'))
    vk_api = vk_session.get_api()

    longpoll = VkLongPoll(vk_session)

    logging.info('VK bot started.')

    redis_db = redis.Redis(
        host=env.str('REDIS_HOST'),
        port=env.int('REDIS_PORT'),
        password=env.str('REDIS_PASSWORD'),
    )

    questions = get_questions('quiz-questions/')

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == '/start':
                start(event, vk_api)
            elif event.text == 'Сдаться':
                give_up(event, vk_api, questions, redis_db)
            elif event.text == 'Новый вопрос':
                ask_question(event, vk_api, questions, redis_db)
            else:
                check_answer(event, vk_api, questions, redis_db)


if __name__ == "__main__":
    main()
