import logging

logger = logging.getLogger(__name__)


def exception_logger(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception('Error occurred while executing function: ' + str(func),
                             extra={'func': str(func), 'exception.name': str(e)})
            raise e

    return wrapper
