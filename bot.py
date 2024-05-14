import logging
import random

from environs import Env
from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackContext)

from main import get_questions


logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )
    custom_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет'],
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text(
        text="Привет! Я бот для викторин!",
        reply_markup=reply_markup
    )


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def ask_question(update: Update, context: CallbackContext) -> None:
    """Ask random question."""
    question_text = random.choice(list(context.bot_data))
    update.message.reply_text(question_text)


def main(questions) -> None:
    """Start the bot."""
    updater = Updater(env.str('TELEGRAM_BOT_TOKEN'))

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.regex(r'Новый вопрос'), ask_question),
    )
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, echo),
    )

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

    quiz_questions = get_questions('quiz-questions/')

    main(quiz_questions)
