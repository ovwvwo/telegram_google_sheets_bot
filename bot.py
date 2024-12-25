import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater, 
    CommandHandler, 
    MessageHandler, 
    Filters, 
    CallbackContext,
    ConversationHandler
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import Dict, List
import threading
import time

# Константы для состояний разговора
CHOOSING_ACTION, ADDING_DATA, SEARCHING_DATA = range(3)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class GoogleSheetsBot:
    def __init__(self, credentials_path: str, spreadsheet_name: str):
        # Настройка доступа к Google Sheets
        self.credentials_path = credentials_path
        self.spreadsheet_name = spreadsheet_name
        self.setup_google_sheets()
        
        # Хранение подписчиков на уведомления
        self.subscribers = set()
        self.last_row_count = len(self.sheet.get_all_values())
        
        # Запуск отслеживания изменений
        self.should_track = True
        self.tracking_thread = threading.Thread(target=self.track_changes)
        self.tracking_thread.daemon = True
        self.tracking_thread.start()
        
        self.reply_keyboard = [
            ['Добавить запись', 'Поиск записи'],
            ['Показать последние записи', 'Подписаться на уведомления'],
            ['Отписаться от уведомлений', 'Помощь']
        ]
        self.markup = ReplyKeyboardMarkup(self.reply_keyboard, one_time_keyboard=True)

    def setup_google_sheets(self):
        """Настройка подключения к Google Sheets"""
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(self.spreadsheet_name).sheet1

    def refresh_google_sheets(self):
        """Обновление подключения к Google Sheets"""
        try:
            self.setup_google_sheets()
        except Exception as e:
            logger.error(f"Ошибка при обновлении подключения: {e}")

    def track_changes(self):
        """Отслеживание изменений в таблице"""
        while self.should_track:
            try:
                current_row_count = len(self.sheet.get_all_values())
                
                if current_row_count > self.last_row_count:
                    # Получаем новые строки
                    new_rows = self.sheet.get_all_values()[self.last_row_count:]
                    
                    # Отправляем уведомления подписчикам
                    for chat_id in self.subscribers:
                        message = "🔔 Новые записи в таблице:\n\n"
                        for row in new_rows:
                            message += f"Дата: {row[0]}\n"
                            message += f"Имя: {row[1]}\n"
                            message += f"Email: {row[2]}\n"
                            message += f"Телефон: {row[3]}\n\n"
                        
                        context = self.updater.dispatcher.bot_data['callback_context']
                        context.bot.send_message(chat_id=chat_id, text=message)
                
                self.last_row_count = current_row_count
                
                # Обновляем подключение каждые 30 минут
                self.refresh_google_sheets()
                
                time.sleep(30)  # Проверяем каждые 30 секунд
                
            except Exception as e:
                logger.error(f"Ошибка при отслеживании изменений: {e}")
                time.sleep(60)  # Если произошла ошибка, ждем минуту перед повторной попыткой

    def subscribe(self, update: Update, context: CallbackContext) -> int:
        """Подписка на уведомления"""
        chat_id = update.effective_chat.id
        if chat_id not in self.subscribers:
            self.subscribers.add(chat_id)
            update.message.reply_text(
                '✅ Вы успешно подписались на уведомления!',
                reply_markup=self.markup
            )
        else:
            update.message.reply_text(
                'Вы уже подписаны на уведомления.',
                reply_markup=self.markup
            )
        return CHOOSING_ACTION

    def unsubscribe(self, update: Update, context: CallbackContext) -> int:
        """Отписка от уведомлений"""
        chat_id = update.effective_chat.id
        if chat_id in self.subscribers:
            self.subscribers.remove(chat_id)
            update.message.reply_text(
                '✅ Вы успешно отписались от уведомлений.',
                reply_markup=self.markup
            )
        else:
            update.message.reply_text(
                'Вы не были подписаны на уведомления.',
                reply_markup=self.markup
            )
        return CHOOSING_ACTION

    def start(self, update: Update, context: CallbackContext) -> int:
        """Начало разговора и показ клавиатуры с действиями"""
        update.message.reply_text(
            'Привет! Я бот для работы с Google Sheets.\n'
            'Выберите действие:',
            reply_markup=self.markup
        )
        return CHOOSING_ACTION

    # ... (остальные методы остаются без изменений)

    def help_command(self, update: Update, context: CallbackContext) -> int:
        """Показать справку"""
        update.message.reply_text(
            'Доступные команды:\n\n'
            '/start - Начать работу с ботом\n'
            'Добавить запись - Добавить новую запись в таблицу\n'
            'Поиск записи - Найти существующие записи\n'
            'Показать последние записи - Показать 5 последних записей\n'
            'Подписаться на уведомления - Получать уведомления о новых записях\n'
            'Отписаться от уведомлений - Прекратить получать уведомления\n'
            'Помощь - Показать это сообщение',
            reply_markup=self.markup
        )
        return CHOOSING_ACTION

def main():
    # Инициализация бота
    bot = GoogleSheetsBot('credentials.json', 'Название вашей таблицы')
    
    # Создание обработчика обновлений
    updater = Updater("ВАШ_ТОКЕН_БОТА")
    bot.updater = updater  # Сохраняем updater для отправки уведомлений
    dispatcher = updater.dispatcher

    # Сохраняем контекст для использования в треде отслеживания
    dispatcher.bot_data['callback_context'] = CallbackContext(dispatcher)

    # Создание обработчика разговора
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', bot.start)],
        states={
            CHOOSING_ACTION: [
                MessageHandler(Filters.regex('^Добавить запись$'), bot.add_data),
                MessageHandler(Filters.regex('^Поиск записи$'), bot.search_data),
                MessageHandler(Filters.regex('^Показать последние записи$'), bot.show_recent),
                MessageHandler(Filters.regex('^Подписаться на уведомления$'), bot.subscribe),
                MessageHandler(Filters.regex('^Отписаться от уведомлений$'), bot.unsubscribe),
                MessageHandler(Filters.regex('^Помощь$'), bot.help_command),
            ],
            ADDING_DATA: [
                MessageHandler(Filters.text & ~Filters.command, bot.save_data)
            ],
            SEARCHING_DATA: [
                MessageHandler(Filters.text & ~Filters.command, bot.perform_search)
            ]
        },
        fallbacks=[CommandHandler('cancel', bot.cancel)]
    )

    dispatcher.add_handler(conv_handler)

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
