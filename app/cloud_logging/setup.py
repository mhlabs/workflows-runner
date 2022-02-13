import logging

import google.cloud.logging

from cloud_logging.filter import GoogleCloudLogFilter
from fastapi.logger import logger


def setup_logging():
    client = google.cloud.logging.Client()
    handler = client.get_default_handler()
    handler.setLevel(logging.DEBUG)
    handler.filters = []
    handler.addFilter(GoogleCloudLogFilter(project=client.project))
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
