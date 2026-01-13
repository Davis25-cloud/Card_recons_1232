import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(log_file='logs/automation.log'):
    os.makedirs('logs', exist_ok=True)
    logger = logging.getLogger("automation")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(log_file, maxBytes=1048576, backupCount=5)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
