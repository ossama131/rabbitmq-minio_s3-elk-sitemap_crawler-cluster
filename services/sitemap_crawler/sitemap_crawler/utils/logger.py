import os
import json
import logging.config
import logging

import sys
sys.path.append("..")

from pythonjsonlogger import jsonlogger

from .init_connections import logs_producer_channel, logs_queue
from .rabbitmq_utils import publish


class RabbitMQHandler(logging.Handler):
    def __init__(self, formatter) -> None:
        super().__init__()
        self.formatter = formatter

    def emit(self, record):
        msg = self.formatter.format(record)
        # msg is already serialized with json.dumps in the formatter, and will be serialized again in publisher
        msg = json.loads(msg)
        publish(logs_producer_channel, logs_queue, msg)


class JsonLogger(object):
    def __init__(self, name:str, level=logging.INFO) -> None:
        self.name = name
        self.level = level
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(level=self.level)
        self.formatter = jsonlogger.JsonFormatter(timestamp=True)

    def getFileLogger(self):
        logs_dir = os.path.abspath(os.getcwd() + '/logs/')
        log_path = os.path.join(logs_dir, self.name + '.log')
        f = open(log_path, 'a+')
        self.logHandler = logging.FileHandler(log_path)
        self.logHandler.setFormatter(self.formatter)
        self.logger.addHandler(self.logHandler)

        return self.logger

    def getRabbitMQLogger(self):
        self.logHandler = RabbitMQHandler(self.formatter)
        self.logger.addHandler(self.logHandler)

        return self.logger

spider_logger = JsonLogger('spider').getRabbitMQLogger()
webclient_logger = JsonLogger('webclient').getRabbitMQLogger()