import logging
import os
import json
from logging.config import dictConfig
import contextvars

request_id_var = contextvars.ContextVar("request_id", default="-")


class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "path"):
            base["path"] = record.path
        if hasattr(record, "method"):
            base["method"] = record.method
        if hasattr(record, "status_code"):
            base["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            base["duration_ms"] = record.duration_ms
        if hasattr(record, "client_ip"):
            base["client_ip"] = record.client_ip
        return json.dumps(base, ensure_ascii=False)


def setup_logging() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "plain")

    plain_format = "%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s (%(module)s:%(lineno)d)"

    if log_format == "json":
        formatter_def = {"()": JsonFormatter}
    else:
        formatter_def = {"format": plain_format, "datefmt": "%Y-%m-%d %H:%M:%S"}

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {"request_id": {"()": RequestIDFilter}},
        "formatters": {
            "default": formatter_def,
            "access": {
                "format": "%(asctime)s %(levelname)s [%(request_id)s] access: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "default",
                "filters": ["request_id"],
                "stream": "ext://sys.stdout",
            },
            "uvicorn_access": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "access",
                "filters": ["request_id"],
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {"handlers": ["console"], "level": log_level, "propagate": True},
            "uvicorn": {"handlers": ["console"], "level": log_level, "propagate": False},
            "uvicorn.error": {"handlers": ["console"], "level": log_level, "propagate": False},
            "uvicorn.access": {"handlers": ["uvicorn_access"], "level": log_level, "propagate": False},
            "app": {"handlers": ["console"], "level": log_level, "propagate": False},
        },
    }

    dictConfig(config)


def set_request_id(request_id: str) -> None:
    request_id_var.set(request_id)


__all__ = ["setup_logging", "request_id_var", "set_request_id"]
