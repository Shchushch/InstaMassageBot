FROM python:3.10

LABEL maintainer='Sergey Karpenko'

# Устанавливаем переменную среды TOKEN со значением, которое будет использоваться внутри контейнера
ENV TOKEN='your_token' ADMIN_USER_ID='your_user_id'

COPY . .

RUN pip install -r requirement.txt

# Запускаем бота при старте контейнера
CMD python Massage_bot.py
