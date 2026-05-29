import logging
from logging.handlers import RotatingFileHandler


def setup_logger(app):
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
    file_handler = RotatingFileHandler('gradeatlas.log', maxBytes=2_000_000, backupCount=5, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
