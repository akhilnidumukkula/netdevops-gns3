IOS_TEMPLATE_ID = "c1d1eb22-c718-4259-ae0a-29c57c5a57bc"
PROJECT_ID = "1cd5351d-f1f8-4ace-9c8a-d2d52ea5ed9f"
GNS3_ROOT_API = "http://192.168.220.129:3080/v2"
GNS3_CONTROLLER_NUM_MAX_CONN = 15
NUM_DEVICES_PER_SWITCH = 50
NUM_SWITCHES_PER_CORE_ROUTER = 100
NUM_DEVICES_PER_ROW = 10
PIXELS_BETWEEN_DEVICES = 85
DOMAIN_NAME = "lab.anidumu.me"
DNS_SERVERS = ["192.168.220.1"]
ENS_NETWORK = "192.168.220.0"
ENS_NET_MASK = "255.255.255.0"
DHCP_CONFIG_TEMPLATE = "dhcp.j2"
ROUTER_CONFIG_TEMPLATE = "router.j2"
START_ROUTER_NUM = 1
END_ROUTER_NUM = 500
DEVICE_USERNAME = "cisco"
DEVICE_PASSWORD = "cisco"
# GNS3_VERSION = 2.2

ANSIBLE_GLOBAL_VARS = {
    "ansible_user": DEVICE_USERNAME,
    "ansible_password": DEVICE_PASSWORD,
    "ansible_connection": "network_cli",
    "ansible_network_os": "ios"
}

NORNIR_DEFAULT_VARS = {
    "username": DEVICE_USERNAME,
    "password": DEVICE_PASSWORD,
    "platform": "ios"
}

LINK_DICT = {
        "capture_compute_id": None,
        "capture_file_name": None,
        "capture_file_path": None,
        "capturing": False,
        "filters": {},
        "link_id": "10bb2efa-4a09-4b64-92c1-716f2482ed3a",
        "link_type": "ethernet",
        "nodes": [
            {
                "adapter_number": 0,
                "label": {
                    "rotation": 0,
                    "style": "font-size: 10; font-style: Verdana",
                    "text": "f0/0",
                    "x": 54,
                    "y": 69
                },
                "node_id": "d3623f62-193e-4206-a1ec-ef934f7b701f",
                "port_number": 0
            },
            {
                "adapter_number": 0,
                "label": {
                    "rotation": 0,
                    "style": "font-size: 10; font-style: Verdana",
                    "text": "e1",
                    "x": -4,
                    "y": -40
                },
                "node_id": "c999f8cf-7478-4a44-87a9-58ed6cdaa127",
                "port_number": 1
            }
        ],
        "project_id": "1cd5351d-f1f8-4ace-9c8a-d2d52ea5ed9f",
        "suspend": False
    }


NODE_DICT = {
    "name": "",
    "properties": {},
    "node_type": "dynamips",
    "node_id": "",
    "compute_id": "local",
    "x": 0,
    "y": 0,
    "z": 1,
    "symbol": ":/symbols/affinity/circle/blue/router.svg",
    "locked": False,
    "label": {
        "text": "",
        "x": 13,
        "y": -25,
        "rotation": 0,
        "style": "font-family: TypeWriter;font-size: 10.0;font-weight: bold;fill: #000000; fill-opacity: 1.0;",
    }
}

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
