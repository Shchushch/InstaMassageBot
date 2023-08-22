FROM python:3.10

LABEL maintainer='Sergey Karpenko'

# Устанавливаем переменную среды TOKEN со значением, которое будет использоваться внутри контейнера
ENV TOKEN='6557394623:AAF75UJVve9U3tcx9huQE7jyF5XlAtU5cY0' ADMIN_USER_ID='445152825'

COPY . .

RUN pip install -r requirement.txt

# Запускаем бота при старте контейнера
CMD python Massage_bot.py
