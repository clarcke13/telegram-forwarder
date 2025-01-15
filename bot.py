from telethon import TelegramClient, events
import time
import os

# Ваши данные (API ID и API Hash)
api_id = '24987362'  # Заменить на твой API ID
api_hash = '266205ada06cb8c1f9cdd6eb452486ed'  # Заменить на твой API Hash

# ID вашей группы, в которой вы пишете сообщения
SOURCE_GROUP_ID = -1001967254470  # Заменить на ID вашей группы

# Задержка для групп из group30.txt (в секундах)
DELAY = 6 * 60 * 60  # 6 часов

# Словари для хранения времени последней отправки сообщений
last_sent_time = {}

# Создаем клиента
client = TelegramClient('session_name', api_id, api_hash)

# Загрузка ID групп из файла
def load_groups(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            groups = []
            for line in file:
                line = line.strip()
                if line:
                    if ',' in line:  # Если строка содержит запятую (группа и ветка)
                        group_id, thread_id = line.split(',')
                        groups.append((int(group_id), int(thread_id)))  # Добавляем кортеж (группа, ветка)
                    else:
                        groups.append((int(line), None))  # Если только группа, ветка None
            return groups
    else:
        print(f"Файл {filename} не найден!")
        return []

# Загружаем группы
IMMEDIATE_GROUPS = load_groups("group.txt")  # Группы с немедленной отправкой
DELAYED_GROUPS = load_groups("group30.txt")  # Группы с задержкой

# Проверка, является ли ваше сообщение последним в группе
async def is_last_message_from_me(group_id):
    try:
        async for message in client.iter_messages(group_id, limit=1):
            if message.sender_id == (await client.get_me()).id:
                print(f"Ваше сообщение является последним в группе {group_id}")
                return True
        return False
    except Exception as e:
        print(f"Ошибка при проверке последнего сообщения в группе {group_id}: {e}")
        return False

# Обработчик сообщений
@client.on(events.NewMessage(chats=SOURCE_GROUP_ID))  # Слушаем только свою группу
async def handler(event):
    message = event.message.text  # Получаем текст сообщения
    if message:  # Проверяем, что сообщение не пустое
        print(f"Сообщение получено: {message}")

        # Отправка в группы с немедленной отправкой (с проверкой последнего сообщения)
        for group in IMMEDIATE_GROUPS:
            group_id, thread_id = group
            if not await is_last_message_from_me(group_id):  # Проверяем последнее сообщение
                try:
                    # Если есть thread_id (ветка), отправляем сообщение в ветку
                    if thread_id:
                        await client.send_message(group_id, message, reply_to=thread_id)
                    else:
                        await client.send_message(group_id, message)
                    print(f"Сообщение отправлено в группу {group_id} (немедленно)")
                except Exception as e:
                    print(f"Не удалось отправить сообщение в группу {group_id}: {e}")
            else:
                print(f"Сообщение в группу {group_id} не отправлено (ваше сообщение уже последнее)")

        # Отправка в группы с задержкой
        current_time = time.time()
        for group in DELAYED_GROUPS:
            group_id, thread_id = group
            last_time = last_sent_time.get(group_id, 0)
            if current_time - last_time >= DELAY:
                if not await is_last_message_from_me(group_id):  # Проверяем последнее сообщение
                    try:
                        # Если есть thread_id (ветка), отправляем сообщение в ветку
                        if thread_id:
                            await client.send_message(group_id, message, reply_to=thread_id)
                        else:
                            await client.send_message(group_id, message)
                        last_sent_time[group_id] = current_time
                        print(f"Сообщение отправлено в группу {group_id} (с задержкой)")
                    except Exception as e:
                        print(f"Не удалось отправить сообщение в группу {group_id}: {e}")
                else:
                    print(f"Сообщение в группу {group_id} не отправлено (ваше сообщение уже последнее)")
            else:
                print(f"Сообщение в группу {group_id} не отправлено (задержка не истекла)")

# Запуск клиента
print("Бот запущен. Ожидание сообщений...")
client.start()
client.run_until_disconnected()