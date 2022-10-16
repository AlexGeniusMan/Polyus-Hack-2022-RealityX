import logging

import json_log_formatter
from agm_env_helper.env_helper import get_env_var
from django.utils import timezone
from dotenv import load_dotenv

load_dotenv()


class CustomisedJSONFormatter(json_log_formatter.JSONFormatter):
    def __init__(self, fmt=None, datefmt=None, style='%', validate=True):
        super(CustomisedJSONFormatter, self).__init__(fmt=None, datefmt=None, style='%', validate=True)

    def json_record(self, message: str, extra: dict, record: logging.LogRecord):
        extra['name'] = record.name
        extra['filename'] = record.filename
        extra['funcName'] = record.funcName
        extra['pathName'] = record.pathname
        extra['msecs'] = record.msecs
        if record.exc_info:
            extra['exc_info'] = self.formatException(record.exc_info)

        return {
            'message': message,
            'timestamp': timezone.now(),
            'log.level': record.levelname,
            'context': extra
        }
