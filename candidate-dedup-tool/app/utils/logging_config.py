import logging
import os
from logging import Logger


def configure_logging(level: int = logging.INFO) -> Logger:
    """Configure logging to console and file `logs/app.log`.

    Returns the root logger.
    """
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'app.log')

    logger = logging.getLogger()
    logger.setLevel(level)

    # avoid adding handlers multiple times
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        sh = logging.StreamHandler()
        sh.setLevel(level)
        sh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
        logger.addHandler(sh)

    if not any(isinstance(h, logging.FileHandler) and getattr(h, 'baseFilename', None) == log_file for h in logger.handlers):
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
        logger.addHandler(fh)

    return logger
