import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

logger = logging.getLogger('GateKeeper')
logger.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(
    filename=BASE_DIR / 'logs' / 'tor.log',
    maxBytes=1024 * 1024,
    backupCount=5)

file_handler.setFormatter(
    logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
