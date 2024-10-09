import logging
from logging.handlers import RotatingFileHandler
import config

# Настройка базового конфигуратора логирования
logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL)
# Форматер логов
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Обработчик для записи логов в файл
file_handler = RotatingFileHandler("log.log", maxBytes=50000000, backupCount=5)
file_handler.setFormatter(formatter)

# Обработчик для вывода логов в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Добавляем обработчики к логгеру
logger.addHandler(file_handler)
logger.addHandler(console_handler)
