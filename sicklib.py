import os
import logging

from functools import wraps
from flask import jsonify, request
from logging.config import dictConfig

logconfig_dict = dict(
    version=1,
    disable_existing_loggers=True,
    root={"level": "INFO", "handlers": []},
    formatters={
        "generic": {
            "format": 'event_time=%(asctime)s process_id=%(process)d loglevel=%(levelname)s file=%(filename)s funcName=%(funcName)s line=%(lineno)d message="%(message)s"',
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            "class": "logging.Formatter",
        }
    },
    loggers={
        "gunicorn.error": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
            "qualname": "gunicorn.error",
        }
    },
    handlers={
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stdout",
        }
    },
)

dictConfig(logconfig_dict)
logger = logging.getLogger("gunicorn.error")


def check_api_key(func):
    """A decorator to validate the microservice API Key on incoming requests."""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        if "X-Api-Key" not in request.headers:
            logger.error("Missing required header, X-Api-Key")
            return jsonify({"result": f"Missing required header, X-Api-Key"}), 400
        if request.headers["X-Api-Key"] != get_cred("MICROSERVICE_API_KEY"):
            logger.error("Invalid API Key")
            return jsonify({"result": "Invalid API Key"}), 400
        return func(*args, **kwargs)

    return decorated_function


def get_cred(name: str) -> str:
    """Get a secret credential by name.

    Args:
        name: The name of the credential.

    Returns:
        The secret credential.
    """
    cred = os.environ.get(name)
    if cred is None:
        logger.error(f"ERROR: `{name}` environment variable could not be loaded.")
    return cred
