# Telegram Bot for EMALL.BY Order Notifications

Telegram-бот для автоматических уведомлений о новых заказах маркетплейса
**EMALL.BY**. Бот получает данные через API маркетплейса, сохраняет информацию
о заказах в SQLite и отправляет пользователям персональные уведомления.

Проект написан на Python с использованием асинхронного фреймворка **aiogram 3**
и упакован в Docker.

## Возможности

- Автоматическое получение новых заказов из API EMALL.BY
- Уведомления пользователей в Telegram о новых заказах
- Регистрация пользователей и хранение их настроек в SQLite
- Интерактивные inline-кнопки и меню бота
- Асинхронная обработка запросов на aiogram 3
- Запуск в Docker без ручной настройки окружения

## Как работает

```text
EMALL.BY API
     │
     ▼
Python-скрипты / планировщик
     │
     ▼
SQLite: заказы и пользователи
     │
     ▼
aiogram 3 Telegram Bot
     │
     ▼
Уведомление пользователю
```

1. Бот или фоновый скрипт обращается к API EMALL.BY.
2. Новые заказы сохраняются в локальную базу SQLite.
3. Для каждого зарегистрированного пользователя формируется уведомление.
4. Бот отправляет сообщение в Telegram.

## Технологии

| Компонент | Технология |
|---|---|
| Telegram Bot | aiogram 3 |
| Язык | Python 3 |
| База данных | SQLite |
| API маркетплейса | EMALL.BY API |
| Контейнеризация | Docker |

## Структура проекта

```text
.
├── handlers.py       # Обработчики команд и сообщений Telegram
├── keyboards.py      # Inline- и reply-клавиатуры
├── scripts.py        # Работа с API EMALL.BY и данными заказов
├── run.py            # Точка входа: запуск бота
├── Dockerfile        # Образ для запуска бота
└── README.md
```

## Быстрый старт

### Локальный запуск

```bash
git clone [https://github.com/alexkarden/telegram-bot-EMALL.BY-sqlite-aiogram3.git](https://github.com/alexkarden/telegram-bot-EMALL.BY-sqlite-aiogram3.git)
cd telegram-bot-EMALL.BY-sqlite-aiogram3

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Создайте файл `.env` или укажите переменные окружения:

```env
BOT_TOKEN=your_telegram_bot_token
EMALL_API_TOKEN=your_emall_api_token
```

Запуск:

```bash
python run.py
```

### Запуск через Docker

```bash
docker build -t emall-telegram-bot .
docker run -d \
  --name emall-bot \
  -e BOT_TOKEN=your_telegram_bot_token \
  -e EMALL_API_TOKEN=your_emall_api_token \
  emall-telegram-bot
```

## Команды бота

| Команда | Описание |
|---|---|
| `/start` | Регистрация пользователя и запуск основного меню |
| `/help` | Справка по работе с ботом |

Также бот использует inline-кнопки для навигации и управления уведомлениями.

## Пример уведомления

```text
🛒 Новый заказ на EMALL.BY

Заказ: #12345
Товар: Пример товара
Сумма: 150 BYN
Статус: Новый
```

## Безопасность

- Токен Telegram-бота и API-ключ EMALL.BY не хранятся в коде.
- Используйте переменные окружения или файл `.env`.
- Добавьте `.env` в `.gitignore`, чтобы не опубликовать секреты.


## Лицензия

MIT
