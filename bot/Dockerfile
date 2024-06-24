# Используем официальный образ Python
FROM python:3.11.9

# Установка зависимостей
RUN apt-get update && apt-get install -y postgresql-client

# Установка рабочей директории в контейнере
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода приложения
COPY . .

# Команда для запуска вашего бота
CMD ["python", "main.py"]