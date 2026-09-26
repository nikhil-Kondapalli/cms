import logging
import sys

from pythonjsonlogger.json import JsonFormatter


def setup_logging():
    handler = logging.StreamHandler(sys.stdout)

    formatter = JsonFormatter("%(asctime)s %(levelname)s %(message)s")

    handler.setFormatter(formatter)

    root = logging.getLogger()

    root.handlers.clear()

    root.addHandler(handler)

    root.setLevel(logging.INFO)
