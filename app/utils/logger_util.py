# app/utils/logger_util.py

import logging
import sys


def get_logger(name="app"):
    from app.utils.env_vars import LOG_LEVEL
    logger = logging.getLogger(name)

    # Set level based on environment
    if LOG_LEVEL == "info":
        logger.setLevel(logging.INFO)
    elif LOG_LEVEL == "debug":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logger.getEffectiveLevel())  # Make sure handler matches logger level

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
