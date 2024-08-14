import telebot
from telebot import types
from datetime import datetime, timedelta
import time
import schedule

# Токены ваших ботов

admin_bot = telebot.TeleBot("7368960650:AAHVOmgtI_unhL4sR213eHhzTIv96wUijlQ")

# Идентификатор чата администраторского бота
admin_chat_id = "1562974695"  # Замените на ID вашего чата

# Идентификатор канала
channel_id = "-1002160441690"  # Замените на ID вашего канала

# Словарь для хранения информации о сообщениях пользователей
user_messages = {}

# Статистика сообщений
total_messages = 0
published_messages = 0




@admin_bot.callback_query_handler(func=lambda call: call.data == "send_photo")
def handle_callback_query(call):
    # Получите информацию о фото
    photo_file_id = call.message.photo[-1].file_id
    caption = call.message.caption

    # Получите идентификатор канала
    channel_id = "-1002160441690"
    message_id = call.message.message_id
    # Перешлите фото в канал
    try:
        admin_bot.send_photo(chat_id=channel_id, photo=photo_file_id, caption=caption)
        admin_bot.delete_message(chat_id=call.message.chat.id, message_id=message_id)
        admin_bot.answer_callback_query(callback_query_id=call.id, text="Фото успешно отправлено!")
    except Exception as e:
        admin_bot.answer_callback_query(callback_query_id=call.id, text="Ошибка при отправке фото.")

# Функция для создания inline клавиатуры
def create_inline_keyboard(photo_file_id):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Отправить в канал", callback_data="send_photo")
    keyboard.add(button)
    return keyboard
# Обработчик callback_query для администраторского бота
@admin_bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    global published_messages
    # Разбираем данные из callback_data
    try:
        action, message_id = call.data.split("_")
    except ValueError:
        # Если callback_data неверный, игнорируем его
        return


    # Проверяем, какая кнопка была нажата
    if action == "publish":
        # Получаем текст сообщения из админского бота
        message_text = call.message.text

        #удаление автоора сообщения
        text = '\n'.join(message_text.splitlines()[1:])

        # Пересылаем сообщение в канал
        admin_bot.send_message(channel_id, text)

        # Меняем текст сообщения на "Сообщение отправлено в канал"
        admin_bot.edit_message_text("Сообщение отправлено в канал!", call.message.chat.id, call.message.message_id)

        # Увеличиваем счетчик отправленных сообщений
        published_messages += 1

    elif action == "skip":
        # Меняем текст сообщения на "Сообщение пропущено"
        admin_bot.edit_message_text("Сообщение пропущено.", call.message.chat.id, call.message.message_id)




# Запускаем ботов
while True:
    try:

        admin_bot.polling(none_stop=True)

        # Выполняем задачи из расписания
        schedule.run_pending()
        time.sleep(1)

    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)
