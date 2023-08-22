import pandas as pd

from config import TOKEN, ADMIN_USER_ID

# Импортируем необходимые модули
# Импортируем необходимые модули
import logging
import asyncio
import time
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from sentence_transformers import SentenceTransformer, InputExample
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Создаем бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Загрузка модели SentenceTransformer
model_name = 'sentence-transformers/msmarco-distilbert-base-tas-b'
model = SentenceTransformer(model_name)

# Загрузка данных и создание векторных представлений
# Путь к вашим данным
data = pd.read_csv('data/Q_and_A_data2 .csv')
train_examples = []
for _, row in data.iterrows():
    question = row['Вопросы']
    answer = row['Ответы']
    train_examples.append(InputExample(texts=[question, answer]))
embeddings = model.encode([example.texts[0] for example in train_examples])

# Функция для обработки входящих сообщений
# Сохранение времени последнего сообщения


GREETING_PHRASES = ["здраст", "привет", "добр"]
THANKS_PHRASES = ['Спасибо', 'Благодарю', 'Ок']

# Настройка логирования
logging.basicConfig(filename='chat_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def handle_user_message(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_query = message.text

    # Проверяем, является ли запрос приветствием
    if any(user_query.lower().startswith(phrase) for phrase in GREETING_PHRASES):
        response = f"Здравствуйте, {user_name}!\n\nЧем я могу помочь?"
        await message.reply(response)
    elif "цена" in user_query.lower() or "записаться" in user_query.lower() or "окошки" in user_query.lower() or "стоит" in user_query.lower():
        response = f"На этот вопрос Вам ответит наш администратор, он свяжется с вами в ближайшее время."
        await message.reply(response)

        # Отправляем администратору уведомление
        admin_user_id = ADMIN_USER_ID  # Замените на фактический ID администратора
        await bot.send_message(admin_user_id, "Клиенту нужна помощь!")

        # Ожидание ответа пользователя
        await asyncio.sleep(10)
        if user_id in last_messages:
            print(f"User {user_name} answered in time.")
        else:
            print(f"User {user_name} did not answer.")
            await bot.send_message(user_id, "Спасибо за проявленный интерес! Мы всегда готовы ответить на ваши вопросы.")
            # await bot.send_message(user_id, "Могу ли я еще чем-то помочь?")
            print(f"Sent thank you message to user {user_name}.")

    else:
        # Получение векторного представления для пользовательского запроса
        user_query_embedding = model.encode([user_query])

        # Вычисление близости между пользовательским запросом и векторами вопросов
        similarities = cosine_similarity(user_query_embedding, embeddings)

        # Находим индексы трех наиболее близких вопросов
        closest_indices = np.argsort(similarities[0])[-3:][::-1]

        # Создаем векторное представление для исходного пользовательского запроса
        original_query_embedding = model.encode([user_query])

        # Вычисление близости между наиболее близкими вопросами и исходным запросом
        similarities_with_original_query = cosine_similarity(
            original_query_embedding, embeddings[closest_indices])

        # Находим индексы трех наиболее близких ответов к наиболее близким вопросам
        closest_answer_indices = np.argsort(
            similarities_with_original_query[0])[-3:][::-1]

        # Формирование и отправка ответа
        response = f"{user_name}!\n"

        # Находим индекс самого близкого ответа
        closest_answer_index = closest_answer_indices[0]

        # response += f"Вопрос: {data.loc[closest_indices[closest_answer_index], 'Вопросы']}\n"
        # response += f"Близость к исходному запросу: {similarities_with_original_query[0][closest_answer_index]:.4f}\n"
        response += f"{data.loc[closest_indices[closest_answer_index], 'Ответы']}\n\n"
        last_messages[user_id] = time.time()
        await message.reply(response)
        # Запись лога
        log_entry = f"User: {user_name} (ID: {user_id})\nQuestion: {user_query}\nBot Response: {response}\n"
        logging.info(log_entry)


# Функция для проверки на неотвеченные сообщения

last_messages = {}


async def check_unanswered_messages():
    while True:
        await asyncio.sleep(15)
        now = time.time()
        for user_id, last_message_time in last_messages.items():
            if now - last_message_time > 10:
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


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    # Создаем задачу проверки неотвеченных сообщений
    loop.create_task(check_unanswered_messages())
    executor.start_polling(dp, skip_updates=True)
