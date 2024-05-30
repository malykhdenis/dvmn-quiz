import logging
import random
from enum import Enum
from functools import partial

import redis
from environs import Env
from telegram import (Update, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackContext, ConversationHandler)

from get_questions import get_questions


logger = logging.getLogger(__name__)

State = Enum('State', ['ASK', 'CHECK'])


def start(update: Update, context: CallbackContext) -> State:
    """Send a message when the command /start is issued."""
    custom_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет'],
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text(
        text="Привет! Я бот для викторин!",
        reply_markup=reply_markup
    )

    return State.ASK


def handle_solution_attempt(
    update: Update,
    context: CallbackContext,
    db: redis.Redis,
) -> None:
    """Check answer in the user message."""
    correct_answer = context.bot_data[
        db.get(update.message.from_user.id).decode('utf-8')
    ]
    if update.message.text == correct_answer['smart_answer']:
        update.message.reply_text('Правильно! Поздравляю!')
        if correct_answer['comment']:
            update.message.reply_text(f'{correct_answer["comment"]}')
        update.message.reply_text(
            'Для следующего вопроса нажми «Новый вопрос».'
        )
    else:
        update.message.reply_text(
            'Неправильно… Попробуешь ещё раз?'
            'Для следующего вопроса нажми «Новый вопрос».'
        )

    return State.ASK


def handle_new_question_request(
        update: Update,
        context: CallbackContext,
        db: redis.Redis,
) -> None:
    """Ask random question."""
    question_text = random.choice(list(context.bot_data))
    db.set(update.message.from_user.id, question_text)
    update.message.reply_text(question_text)

    return State.CHECK


def give_up(
    update: Update,
    context: CallbackContext,
    db: redis.Redis
) -> None:
    """Get answer and another question."""
    correct_answer = context.bot_data[
        db.get(update.message.from_user.id).decode('utf-8')
    ]['answer']
    update.message.reply_text(correct_answer)
    next_question = random.choice(list(context.bot_data))
    db.set(update.message.from_user.id, next_question)
    update.message.reply_text(next_question)

    return State.CHECK


def cancel(update: Update, context: CallbackContext) -> None:
    """Cancel conversation."""
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main(token: str, questions: dict) -> None:
    """Start the bot."""
    updater = Updater(token)

    dispatcher = updater.dispatcher

    redis_db = redis.Redis(
        host=env.str('REDIS_HOST'),
        port=env.int('REDIS_PORT'),
        password=env.str('REDIS_PASSWORD'),
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            State.ASK: [
                MessageHandler(
                    Filters.regex(r'Новый вопрос'),
                    partial(handle_new_question_request, db=redis_db),
                ),
            ],
            State.CHECK: [
                MessageHandler(
                    Filters.regex(r'Сдаться'),
                    partial(give_up, db=redis_db),
                ),
                MessageHandler(
                    Filters.text & ~Filters.command,
                    partial(handle_solution_attempt, db=redis_db),
                ),
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)

    dispatcher.bot_data = questions

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )

    env = Env()
    env.read_env()

    telegram_token = env.str('TELEGRAM_BOT_TOKEN')

    quiz_questions = get_questions('quiz-questions/')

    main(telegram_token, quiz_questions)
