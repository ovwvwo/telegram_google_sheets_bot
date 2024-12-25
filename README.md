# telegram_google_sheets_bot
Наброски на питоне Автоматизация задач с Google Sheets: Разработайте бота, который будет взаимодействовать с Google Sheets через Telegram. Это включает автоматическое обновление данных или отправку уведомлений о изменениях

Создано с любовью...и большим количесвом ошибок :heart:
# Telegram Bot с интеграцией Google Sheets
## Документация

### Содержание
1. [Обзор](#обзор)
2. [Установка](#установка)
3. [Конфигурация](#конфигурация)
4. [Функциональность](#функциональность)
5. [API Reference](#api-reference)
6. [Структура проекта](#структура-проекта)
7. [Требования](#требования)
8. [Развертывание](#развертывание)
9. [Обслуживание](#обслуживание)

### Обзор
Telegram бот для автоматизации работы с Google Sheets. Позволяет добавлять, искать данные и получать уведомления об изменениях в таблице в реальном времени.

### Установка
```bash
# Клонирование репозитория
git clone https://github.com/...

# Установка зависимостей
pip install -r requirements.txt
```

Содержимое requirements.txt:
```
python-telegram-bot==13.7
gspread==5.7.1
oauth2client==4.1.3
```

### Конфигурация
1. **Google Sheets API**
   - Создайте проект в Google Cloud Console
   - Включите Google Sheets API
   - Создайте Service Account
   - Загрузите credentials.json
   - Предоставьте доступ к таблице для service account email

2. **Telegram Bot**
   - Получите токен бота у @BotFather
   - Создайте config.py:
   ```python
   TELEGRAM_TOKEN = "ваш_токен"
   SPREADSHEET_NAME = "название_таблицы"
   CREDENTIALS_PATH = "путь/к/credentials.json"
   ```

3. **Структура Google Sheets**
   ```
   | Timestamp | Name | Email | Phone |
   |-----------|------|-------|-------|
   ```

### Функциональность
1. **Основные команды**
   - /start - Запуск бота
   - /cancel - Отмена текущей операции

2. **Работа с данными**
   - Добавление записей
   - Поиск по записям
   - Просмотр последних записей
   - Подписка на уведомления
   - Отписка от уведомлений

3. **Система уведомлений**
   - Автоматическое отслеживание изменений
   - Push-уведомления подписчикам
   - Обновление подключения каждые 30 минут

### API Reference
#### GoogleSheetsBot
```python
class GoogleSheetsBot:
    def __init__(self, credentials_path: str, spreadsheet_name: str)
    def setup_google_sheets() -> None
    def refresh_google_sheets() -> None
    def track_changes() -> None
    def subscribe(update: Update, context: CallbackContext) -> int
    def unsubscribe(update: Update, context: CallbackContext) -> int
```

### Структура проекта
```
telegram-sheets-bot/
├── main.py
├── config.py
├── requirements.txt
├── credentials.json
├── README.md
└── logs/
    └── bot.log
```

### Требования
- Python 3.7+
- Доступ к Google Cloud Platform
- Telegram Bot API Token
- Стабильное интернет-соединение

### Развертывание
1. **Локальное развертывание**
   ```bash
   python main.py
   ```

2. **Docker развертывание**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   CMD ["python", "main.py"]
   ```

   ```bash
   docker build -t telegram-sheets-bot .
   docker run -d telegram-sheets-bot
   ```

### Обслуживание
1. **Логирование**
   - Все события записываются в logs/bot.log
   - Уровень логирования: INFO

2. **Мониторинг**
   - Отслеживание состояния подключения к Google Sheets
   - Автоматическое переподключение при ошибках
   - Уведомления об ошибках в логах

3. **Обработка ошибок**
   - Автоматический реконнект к Google Sheets
   - Повторные попытки при сбоях
   - Сохранение состояния подписчиков

4. **Безопасность**
   - Используйте переменные окружения для токенов
   - Регулярно обновляйте credentials.json
   - Ограничьте доступ к таблице

5. **Бэкапы**
   - Регулярное резервное копирование базы подписчиков
   - Сохранение логов
