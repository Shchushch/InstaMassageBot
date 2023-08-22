# Шаблон для бота

import logging
import asyncio
import time

from aiogram import Bot, Dispatcher, executor, types

from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


# Словарь для хранения времен последних сообщений от пользователей
last_messages = {}

# Обработка любого входящего сообщения


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def handle_any_message(message: types.Message):
    # Получение имени пользователя
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # Ожидание 10 секунд
    await asyncio.sleep(10)

    # Формирование ответа
    response = f"Здравствуйте, {user_name}! Чем я могу помочь?"

    # Отправка ответа пользователю
    await message.reply(response)

    # Сохранение времени последнего сообщения
    last_messages[user_id] = time.time()

# Проверка на неотвеченные сообщения


async def check_unanswered_messages():
    while True:
        await asyncio.sleep(15)
        now = time.time()
        for user_id, last_message_time in last_messages.items():
            if now - last_message_time > 15:
                # Отправляем вопрос, если прошло более 15 секунд после последнего сообщения
                user_name = (await bot.get_chat(user_id)).first_name
                await bot.send_message(user_id, f"{user_name}, у Вас еще остались вопросы?")
                del last_messages[user_id]
                await asyncio.sleep(10)  # Ожидание 10 секунд
                if user_id in last_messages:
                    # Если пользователь ответил в течение 10 секунд, завершаем функцию
                    continue
                # Отправляем благодарность за проявленный интерес
                await bot.send_message(user_id, f"Спасибо, {user_name}, за проявленный интерес! Мы всегда готовы ответить на ваши вопросы.")

# Запуск бота и проверки на неотвеченные сообщения
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.create_task(check_unanswered_messages())
    executor.start_polling(dp, skip_updates=True)


#    # Ожидание ответа пользователя
#         await asyncio.sleep(10)
#         if user_id in last_messages:
#             print(f"User {user_name} answered in time.")
#         else:
#             print(f"User {user_name} did not answer.")
#             await bot.send_message(user_id, "Спасибо за проявленный интерес! Мы всегда готовы ответить на ваши вопросы.")
#             # await bot.send_message(user_id, "Могу ли я еще чем-то помочь?")
#             print(f"Sent thank you message to user {user_name}.")


# last_messages = {}


# async def check_unanswered_messages():
#     while True:
#         now = time.time(5)
#         print("Checking unanswered messages...")
#         for user_id, last_message_time in last_messages.items():
#             if now - last_message_time > 8:
#                 try:
#                     user_name = (await bot.get_chat(user_id)).first_name
#                     print(f"User {user_name} has unanswered messages.")
#                     await bot.send_message(user_id, f"{user_name}, у Вас еще остались вопросы?")
#                     del last_messages[user_id]
#                     print(
#                         f"Removed user {user_name} from unanswered messages list.")

#                     await asyncio.sleep(10)
#                     if user_id in last_messages:
#                         print(f"User {user_name} answered in time.")
#                     else:
#                         print(f"User {user_name} did not answer.")
#                         await bot.send_message(user_id, f"Спасибо, {user_name}, за проявленный интерес! Мы всегда готовы ответить на ваши вопросы.")
#                         # await bot.send_message(user_id, "С удовольствием на них отвечу")
#                         print(f"Sent thank you message to user {user_name}.")
#                 except Exception as e:
#                     print(f"An error occurred: {e}")
#                     # Дополнительная обработка ошибок, например, логирование
#                     pass

# from config import TOKEN, ADMIN_USER_ID
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
