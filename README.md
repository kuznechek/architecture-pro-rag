# Задание 1. Исследование моделей и инфраструктуры

[Исследование моделей и инфраструктуры](https://github.com/kuznechek/architecture-pro-rag/blob/rag/task1.md)

# Задание 2. Подготовка базы знаний

Выбранные статьи:

[Сохранённые статьи](https://github.com/kuznechek/architecture-pro-rag/blob/rag/knowledge_base/articles_sw.md)

[Термины](https://github.com/kuznechek/architecture-pro-rag/blob/rag/knowledge_base/terms.json)

[Словарь терминов с новыми значениями (из мира Властелин Колец)](https://github.com/kuznechek/architecture-pro-rag/blob/rag/knowledge_base/terms_map.json)

[Статьи, в которых произведены замены](https://github.com/kuznechek/architecture-pro-rag/blob/rag/knowledge_base/acticles_lotr.md)

# Задание 3. Создание векторного индекса базы знаний

**Название модели :** all-MiniLM-L6-v2

**Ссылка на репозиторий / API :** [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

**Размер эмбеддингов :** 384

**Класс ОПП, отвечающий за преобразование текста в чанки, генерацию эмбеддингов и индексацию в FAISS :**
[indexer.py](https://github.com/kuznechek/architecture-pro-rag/blob/rag/task3/indexer.py)

**Скрипт, с помощью которого создавался и сохранялся индекс :**
[build_index.py](https://github.com/kuznechek/architecture-pro-rag/blob/rag/task3/build_index.py)

Для запуска:

```
pip install -r requirements.txt

python build_index.py
```

**Скрипт запроса по индексу :**
[find_index.py](https://github.com/kuznechek/architecture-pro-rag/blob/rag/task3/find_index.py)

```
python find_index.py
```

# Задание 4. Реализация RAG-бота с техниками промптинга

Загрузка модели llama3.1 :

```
docker exec ollama ollama pull llama3.1

```

Для запуска бота :

```
docker-compose up -d

```

Посмотреть лог бота :

```
docker logs -f rag-bot

```

Проверить сервис :

```
Invoke-RestMethod http://localhost:8001/health
Invoke-RestMethod http://localhost:8001/test

```

![Запросы](https://github.com/kuznechek/architecture-pro-rag/blob/rag/task4/src/test_query.png)

Лог:

![Лог](https://github.com/kuznechek/architecture-pro-rag/blob/rag/task4/src/test_log.png)

## BASE

```
Invoke-RestMethod -Uri http://localhost:8001/ask -Method Post -ContentType "application/json" -Body '{"question": "Who is Sauron?", "prompt_type": "base"}'

```

![Запрос](https://github.com/kuznechek/architecture-pro-rag/blob/rag/task4/src/base_answer.png)

## FEW SHOT

```
Invoke-RestMethod -Uri http://localhost:8001/ask -Method Post -ContentType "application/json" -Body '{"question": "Who is Sauron?", "prompt_type": "few_shot"}'

```

![Запрос](https://github.com/kuznechek/architecture-pro-rag/blob/rag/task4/src/few_shot_answer.png)

## COT

```
Invoke-RestMethod -Uri http://localhost:8001/ask -Method Post -ContentType "application/json" -Body '{"question": "Who is Sauron?", "prompt_type": "cot"}'

```

![Запрос](https://github.com/kuznechek/architecture-pro-rag/blob/rag/task4/src/cot_answer.png)

# Задание 5. Запуск и демонстрация работы бота

# Задание 6. Автоматическое ежедневное обновление базы знаний

# Задание 7. Аналитика покрытия и качества базы знаний