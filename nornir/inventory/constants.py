LOGGING_DICT = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "std-module": {
            "format": "[%(asctime)s] %(levelname)-8s {%(name)s:%(lineno)d} %(message)s"
        },
        "std": {
            "format": "[%(asctime)s] %(levelname)-8s {%(filename)s:%(lineno)d} %(message)s"
        }
    },
    "handlers": {
        "file-module": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "app.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "std-module",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "app.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "std",
        },
        "console-module": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "std-module",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "std",
        },
    },
    "loggers": {
        "netmiko": {
            "handlers": ["console-module"],
            "level": "WARNING",
            "propagate": False
        },
        "paramiko": {
            "handlers": ["console-module"],
            "level": "WARNING",
            "propagate": False
        },
        "app": {
            "handlers": ["console-module", "file-module"],
            "level": "DEBUG",
            "propagate": False
        }
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
}