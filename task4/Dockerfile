FROM python:3.11

WORKDIR /app

# Установка системных зависимостей (для FAISS и sentence-transformers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода бота
COPY RAGBot.py PromtBuilder.py api.py ./

# Открываем порт для API
EXPOSE 8001

# Запуск API сервера
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]