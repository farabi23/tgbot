import datetime
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
import time
import sys
import config

# Define conversation states
SELECTING_REMINDER, SELECTING_DATE, SELECTING_NOTICE = range(3)

def start(update, context):

    reply_keyboard = [['Кредит', 'Дедлайн по учебе', 'Сдача проекта', 'Отмена']]


    update.message.reply_text(
        "Привет! Я бот для напоминаний по дедлайнам. Введите вид ремайндера:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SELECTING_REMINDER

def select_reminder(update, context):
    user = update.message.from_user
    reminder = update.message.text
    context.user_data['reminder'] = reminder
    update.message.reply_text("Вы выбрали: {}. Введите дату дедлайна (в формате дд-мм-гггг):".format(reminder))
    return SELECTING_DATE


def select_date(update, context):
    user = update.message.from_user
    deadline_date = datetime.datetime.strptime(update.message.text, '%d-%m-%Y').date()
    context.user_data['deadline_date'] = deadline_date
    reply_keyboard = [['7', '5', '3'], ['2', '1']]
    update.message.reply_text(
        "Введите срок за который нужно предупредить (в днях):",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SELECTING_NOTICE

def select_notice(update, context):
    user = update.message.from_user
    notice = int(update.message.text)
    context.user_data['notice'] = notice
    update.message.reply_text(
        "Привет! У тебя {} подходит к заданному сроку через {} дней! Хочешь перенести срок напоминания?".format(
            context.user_data['reminder'], notice
        ),
        reply_markup=ReplyKeyboardMarkup([['Да', 'Нет']], one_time_keyboard=True)
    )
    return SELECTING_NOTICE

def remind_later(update, context):
    user = update.message.from_user
    update.message.reply_text(
        "Хорошо! Я напомню на следующий день. Я надеюсь, ты закончил свои задачи."
        "Не хочешь ли добавить ещё что-нибудь или повторить это напоминание в следующем месяце?",
        reply_markup=ReplyKeyboardMarkup([['Да', 'Нет', 'Добавить новое']], one_time_keyboard=True)
    )
    return SELECTING_NOTICE

def end_conversation(update, context):
    user = update.message.from_user
    if update.message.text == 'Добавить новое':
        return start(update, context)
    else:
        update.message.reply_text("Хорошо! До свидания!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


def main():
    token = config.TOKEN
    updater = Updater(token)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_REMINDER: [MessageHandler(Filters.text & ~Filters.command, select_reminder)],
            SELECTING_DATE: [MessageHandler(Filters.regex(r'^\d{2}-\d{2}-\d{4}$'), select_date)],
            SELECTING_NOTICE: [MessageHandler(Filters.regex(r'^[0-9]$'), select_notice)]
        },
        fallbacks=[MessageHandler(Filters.regex(r'^(Отмена|Нет|Да|Добавить новое)$'), end_conversation)]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
