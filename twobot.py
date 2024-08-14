import telebot
from telebot import types
from datetime import datetime, timedelta
import time
import schedule
import os
# Токены ваших ботов
bot = telebot.TeleBot("7343479877:AAFcx2mB6d-S5NEqJp7-BSBW5HzBA7ypfks")
admin_bot = telebot.TeleBot("7368960650:AAHVOmgtI_unhL4sR213eHhzTIv96wUijlQ")

# Идентификатор чата администраторского бота
admin_chat_id = "1562974695"  # Замените на ID вашего чата

# Идентификатор канала
channel_id = "-1002065455575"  # Замените на ID вашего канала

# Словарь для хранения информации о сообщениях пользователей
user_messages = {}

# Статистика сообщений
total_messages = 0
published_messages = 0
save_dir = 'photos'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
def send_weekly_stats():
    global total_messages, published_messages

    # Вычисляем процент отправленных сообщений
    if total_messages == 0:
        percentage_published = 0
    else:
        percentage_published = round((published_messages / total_messages) * 100, 2)

    # Отправляем сообщение администратору
    admin_bot.send_message(
        admin_chat_id,
        f"Статистика за прошлую неделю:\n\n"
        f"Всего сообщений: {total_messages}n"
        f"Отправлено в канал: {published_messages} ({percentage_published}%)\n"
        f"Пропущено: {total_messages - published_messages} ({100 - percentage_published}%)\n"
    )

    # Сбрасываем счетчики статистики
    total_messages = 0
    published_messages = 0
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    global total_messages
    user_id = message.from_user.id

    # Проверяем, есть ли запись о пользователе в словаре
    if user_id not in user_messages:
        user_messages[user_id] = {
            "last_message_time": datetime.now() - timedelta(hours=1),  # Инициализация времени последнего сообщения
            "message_count": 0
        }

    # Проверяем, прошло ли 1 час с последнего сообщения
    if datetime.now() - user_messages[user_id]["last_message_time"] > timedelta(minutes=20):
        user_messages[user_id]["message_count"] = 0  # Сбрасываем счетчик сообщений

    # Проверяем, не превышен ли лимит сообщений
    if user_messages[user_id]["message_count"] >= 3:
        # Вычисляем время, когда можно будет отправить следующее сообщение
        next_message_time = user_messages[user_id]["last_message_time"] + timedelta(minutes=20)
        time_remaining = next_message_time - datetime.now()

        # Форматируем время для вывода
        time_remaining_str = time_remaining.seconds // 3600
        if time_remaining_str > 0:
            time_remaining_str += " час"
        else:
            time_remaining_str = str((time_remaining.seconds // 60) % 60) + " минут"

        # Отправляем сообщение пользователю
        bot.send_message(message.chat.id,
                         f"Извините, вы можете отправить не более 3 сообщений за 20 минут. Следующее сообщение можно будет отправить через {time_remaining_str}.")
        return

    # Пересылаем сообщение в администраторский бот с кнопками
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Отправить в канал", callback_data=f"send_photo")

    markup.add(item1)
    # Получаем файл фотографии
    photo_file = message.photo[-1].file_id

    # Скачиваем фото
    file_info = bot.get_file(photo_file)
    downloaded_file = bot.download_file(file_info.file_path)

    # Сохраняем фото
    filename = f"{message.chat.id}_{int(time.time())}.jpg"
    filepath = os.path.join(save_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(downloaded_file)

    # Получаем текст подписи
    caption = message.caption

    # Отправляем фото с подписью второму боту
    try:
        with open(filepath, 'rb') as f:
            admin_bot.send_photo(chat_id="1562974695", photo=f, caption=caption, reply_markup=markup)  # Замените на ID канала
            bot.send_message(message.chat.id, "Фото сохранено и отправлено!")
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка при отправке фото. Попробуйте позже.")
    # Обновляем информацию о сообщении пользователя
    user_messages[user_id]["last_message_time"] = datetime.now()
    user_messages[user_id]["message_count"] += 1

    # Увеличиваем счетчик всех сообщений
    total_messages += 1
    # Список расширений фото
    photo_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

    # Проход по всем файлам в папке
    for filename in os.listdir(save_dir):
        # Проверяем расширение файла
        if any(filename.endswith(ext) for ext in photo_extensions):
            file_path = os.path.join(save_dir, filename)
            try:
                os.remove(file_path)
                print(f'Файл {filename} удалён успешно.')
            except Exception as e:
                print(f'Ошибка при удалении файла {filename}: {e}')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я анонимный бот. Пишите мне сообщения, и я отправлю их администратору.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global total_messages
    user_id = message.from_user.id

    # Проверяем, есть ли запись о пользователе в словаре
    if user_id not in user_messages:
        user_messages[user_id] = {
            "last_message_time": datetime.now() - timedelta(hours=1),  # Инициализация времени последнего сообщения
            "message_count": 0
        }

    # Проверяем, прошло ли 1 час с последнего сообщения
    if datetime.now() - user_messages[user_id]["last_message_time"] > timedelta(minutes=5):
        user_messages[user_id]["message_count"] = 0  # Сбрасываем счетчик сообщений

    # Проверяем, не превышен ли лимит сообщений
    if user_messages[user_id]["message_count"] >= 3:
        # Вычисляем время, когда можно будет отправить следующее сообщение
        next_message_time = user_messages[user_id]["last_message_time"] + timedelta(minutes=5)
        time_remaining = next_message_time - datetime.now()

        # Форматируем время для вывода
        time_remaining_str = time_remaining.seconds // 3600
        if time_remaining_str > 0:
            time_remaining_str += " час"
        else:
            time_remaining_str = str((time_remaining.seconds // 60) % 60) + " минут"

        # Отправляем сообщение пользователю
        bot.send_message(message.chat.id,
                         f"Извините, вы можете отправить не более 3 сообщений в час. Следующее сообщение можно будет отправить через {time_remaining_str}.")
        return

    # Пересылаем сообщение в администраторский бот с кнопками
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Отправить в канал", callback_data=f"publish_{message.message_id}")
    item2 = types.InlineKeyboardButton("Пропустить", callback_data=f"skip_{message.message_id}")
    markup.add(item1, item2)
    admin_bot.send_message(admin_chat_id, f"Новое сообщение от @{message.from_user.username}:\n{message.text}",
                           reply_markup=markup)
    # Отправляем сообщение пользователю о том, что его сообщение переслано
    bot.send_message(message.chat.id, "Ваше сообщение успешно отправлено администратору.")
    # Обновляем информацию о сообщении пользователя
    user_messages[user_id]["last_message_time"] = datetime.now()
    user_messages[user_id]["message_count"] += 1

    # Увеличиваем счетчик всех сообщений
    total_messages += 1


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


# Настройка расписания для отправки еженедельной статистики
schedule.every().tuesday.at("20:50").do(send_weekly_stats)

# Запускаем ботов
while True:
    try:
        print("""
        ███████████▓▓▓▓▓▓▓▓▒░░░░░▒▒░░░░░░░▓█████
        ██████████▓▓▓▓▓▓▓▓▒░░░░░▒▒▒░░░░░░░░░░▓████
        █████████▓▓▓▓▓▓▓▓▒░░░░░░▒▒▒░░░░░░░░░▓███
        ████████▓▓▓▓▓▓▓▓▒░░░░░░░▒▒▒░░░░░░░░░░███
        ███████▓▓▓▓▓▓▓▓▒░░▒▓░░░░░░░░░░░░░░░░░███
        ██████▓▓▓▓▓▓▓▓▒░▓████░░░░░▒▓░░░░░░░░░███
        █████▓▒▓▓▓▓▓▒░▒█████▓░░░░▓██▓░░░░░░░▒███
        ████▓▒▓▒▒▒░░▒███████░░░░▒████░░░░░░░░███
        ███▓▒▒▒░░▒▓████████▒░░░░▓████▒░░░░░░▒███
        ██▓▒▒░░▒██████████▓░░░░░▓█████░░░░░░░███
        ██▓▒░░███████████▓░░░░░░▒█████▓░░░░░░░███
        ██▓▒░▒██████████▓▒▒▒░░░░░██████▒░░░░░▓██
        ██▓▒░░▒███████▓▒▒▒▒▒░░░░░▓██████▓░░░░▒██
        ███▒░░░░▒▒▒▒▒▒▒▒▒▒▒▒░░░░░░███████▓░░░▓██
        ███▓░░░░░▒▒▒▓▓▒▒▒▒░░░░░░░░░██████▓░░░███
        ████▓▒▒▒▒▓▓▓▓▓▓▒▒▓██▒░░░░░░░▓███▓░░░░███
        ██████████▓▓▓▓▒▒█████▓░░░░░░░░░░░░░░████
        █████████▓▓▓▓▒▒░▓█▓▓██░░░░░░░░░░░░░█████
        ███████▓▓▓▓▓▒▒▒░░░░░░▒░░░░░░░░░░░░██████
        ██████▓▓▓▓▓▓▒▒░░░░░░░░░░░░░░░░▒▓████████
        ██████▓▓▓▓▓▒▒▒░░░░░░░░░░░░░░░▓██████████
        ██████▓▓▓▓▒▒██████▒░░░░░░░░░▓███████████
        ██████▓▓▓▒▒█████████▒░░░░░░▓████████████
        ██████▓▓▒▒███████████░░░░░▒█████████████
        ██████▓▓░████████████░░░░▒██████████████
        ██████▓░░████████████░░░░███████████████
        ██████▓░▓███████████▒░░░████████████████
        ██████▓░███████████▓░░░█████████████████
        ██████▓░███████████░░░██████████████████
        ██████▓▒██████████░░░███████████████████
        ██████▒▒█████████▒░▓████████████████████
        ██████░▒████████▓░██████████████████████
        ██████░▓████████░███████████████████████
        ██████░████████░▒███████████████████████
        █████▓░███████▒░████████████████████████
        █████▒░███████░▓████████████████████████
        █████░▒██████░░█████████████████████████
        █████░▒█████▓░██████████████████████████
        █████░▓█████░▒██████████████████████████
        █████░▓████▒░███████████████████████████
        █████░▓███▓░▓███████████████████████████
        ██████░▓▓▒░▓████████████████████████████
        ███████▒░▒██████████████████████████████
        ████████████████████████████████████████
        ████████████████████████████████████████""")


        bot.polling(none_stop=True)
        admin_bot.polling(none_stop=True)


        # Выполняем задачи из расписания
        schedule.run_pending()
        time.sleep(1)

    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)