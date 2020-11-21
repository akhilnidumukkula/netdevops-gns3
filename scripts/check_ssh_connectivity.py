import logging
import logging.config
from concurrent.futures import ThreadPoolExecutor
from netmiko import ConnectHandler

from app.constants import LOGGING_DICT, DEVICE_USERNAME, DEVICE_PASSWORD
from app.lab import Lab
from app.device import Device

logger = logging.getLogger(__name__)


def check_ssh_connectivity(device: Device):
    params = {
        'host': device.mgmt_int_ip,
        'username': DEVICE_USERNAME,
        'password': DEVICE_PASSWORD,
        'device_type': 'cisco_ios'
    }
    logger.info("Attempting to connect to %r", device.name)
    with ConnectHandler(**params) as conn:
        _ = conn.find_prompt()
        

def main():
    lab = Lab.create()
    with ThreadPoolExecutor(max_workers=250) as pool:
        results = pool.map(check_ssh_connectivity, lab.devices)
    _ = [result for result in results]
    
    
if __name__ == '__main__':
    logging.config.dictConfig(LOGGING_DICT)
    main()