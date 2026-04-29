FROM python:3.11-slim

WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Копируем все файлы проекта
COPY . .

# Убеждаемся, что папка assets существует
RUN mkdir -p assets

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Запуск приложения
CMD ["gunicorn", "app:server", "--bind", "0.0.0.0:7860", "--workers", "1", "--threads", "2", "--timeout", "300", "--access-logfile", "-", "--error-logfile", "-"]