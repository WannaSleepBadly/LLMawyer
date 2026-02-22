# Telegram Juridical Bot

Telegram-бот юрист, который принимает голосовые или текстовые сообщения и с помощью LLM и RAG даёт ответы о законодательстве РФ.


## Установка и настройка

### 1. Установка PostgreSQL и Milvus

```bash
# Скачайте и установите PostgreSQL с официального сайта
# https://www.postgresql.org/download/windows/
curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh
bash standalone_embed.sh start
```

### 2. Создание postgres базы данных

```bash
# Подключение к PostgreSQL
psql -U postgres

# Создание базы данных
CREATE DATABASE llmawyer;
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Внесите данные из env.txt в файл `.env` в корне проекта.

### 5. Парсинг закона
```bash
python law_data.law_parser
```
В результате будет получен `laws.json` с текстами законов. 

### 6. Занесение данных в postgres
```bash
python law_data.repository
```

### 7. Заполнение milvus
Запустите docker контейнер с milvus
```bash
python -m agent.setup.init_milvus
```

### 8. Запуск

```bash
python bot.bot.py
```

## Структура базы данных

### Таблица `laws`
- `law_id` - Уникальный идентификатор закона
- `name` - Название закона
- `code` - Номер ФЗ (например, "38-FZ")
- `source_url` - Ссылка на источник
- `created_at` - Дата загрузки

### Таблица `law_chapters`
- `chapter_id` - Уникальный идентификатор главы
- `law_id` - Ссылка на закон
- `number` - Номер главы
- `title` - Название главы
- `source_url` - Ссылка на источник

### Таблица `law_parts`
- `part_id` - Уникальный идентификатор статьи
- `chapter_id` - Ссылка на главу
- `number` - Номер статьи
- `title` - Название статьи
- `source_url` - Ссылка на источник

### Таблица `law_paragraphs`
- `paragraph_id` - Уникальный идентификатор пункта
- `part_id` - Ссылка на статью
- `paragraph_number` - Номер пункта
- `content` - Исходный текст пункта

## Примеры ответов

```
🎤 Транскрипция: Что нужно знать при размещении рекламы в интернете?

🤖 Ответ: реклама должна соответствовать общим нормам, изложенным в статье 5 части 1 ФЗ О рекламе. \
Согласно статье 18.2 части 2 рекламодатель должен платить налог с доходов от рекламы.
```

```
🎤 Транскрипция: О чём пункт 1 части 5 статьи 5 главы 1 ФЗ О рекламе?

🤖 Ответ: Пункт 1 части 5 статьи 5 главы 1 ФЗ О рекламе гласит, что в рекламе не должно быть иностранных слов.
```

## Технологии

- **Python Telegram Bot** - основной фреймворк для бота
- **Postgres** - хранение текстов и мета-данных
- **Milvus** - хранение эмбеддингов 
- **OpenAI Whisper** - транскрипция голосовых сообщений
- **SentenceTransformers** - получение текстовых эмбеддингов
- **CUDA** - ускорение моделей на GPU
- **FFmpeg** - обработка аудио файлов
- **Python asyncio** - асинхронная обработка
- **Logging** - подробное логирование всех операций

