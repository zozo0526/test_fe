import logging
from logging import DEBUG, INFO, ERROR, WARNING, CRITICAL
from logging.handlers import RotatingFileHandler

from env_config import load_env

debug = DEBUG
info = INFO
warning = WARNING
error = ERROR
critical = CRITICAL

# log_level_from_env = load_env(".env")["LOG_LEVEL"]


def configure_logger(name, log_file, level):
    """
    Configure the custom logger that presents with datetime, level, name, and message.
    :param name: The name that shows up in the log, e.g. __name__ (the name of the current module)
    :param log_file: If you want to log to a file, specify the file name here
    :param level: The log level, e.g. logging.DEBUG/ logging.INFO/ logging.ERROR
    :return my_logger:
    Usage example:
    logger = configure_logger(__name__, 'deploy.log', level=logging.DEBUG)
    """
    # Parameters:
    #   - filename: The name of the log file.
    #   - maxBytes: The maximum file size (in bytes) before it gets rotated.
    #   - backupCount: The number of backup files to keep.

    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024,
                                  backupCount=3)  # 5 MB per log file, keep 3 old logs

    my_logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()  # Log to console
    stream_handler.setFormatter(formatter)

    my_logger.setLevel(level)
    my_logger.addHandler(file_handler)
    my_logger.addHandler(stream_handler)

    return my_logger
