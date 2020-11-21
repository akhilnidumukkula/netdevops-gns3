from concurrent.futures import ThreadPoolExecutor
import logging
import logging.config

from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.base_connection import BaseConnection

from app.constants import LOGGING_DICT, DEVICE_USERNAME, DEVICE_PASSWORD
from app.lab import Lab
from app.device import Device
from app import utils

logger = logging.getLogger(__name__)

def is_ssh_enabled(conn: BaseConnection, device_name: str) -> bool:
    prompt = f"{device_name}#"
    sh_ip_ssh_output = conn.send_command("sh ip ssh", expect_string=prompt)
    if "SSH Enabled - version 2.0" in sh_ip_ssh_output:
        return True
    else:
        return False
    

@utils.retry((NetMikoTimeoutException, OSError, ValueError), max_retries=2)
def generate_crypto_key(device: Device):
    params = {
        'host': device.mgmt_int_ip,
        'username': DEVICE_USERNAME,
        'password': DEVICE_PASSWORD,
        'device_type': 'cisco_ios_telnet'
    }
    # logger.info("Attempting to connect to %r", device.name)
    with ConnectHandler(**params) as conn:
        if is_ssh_enabled(conn, device.name):
            logger.info("Router %r - SSH v2 is already enabled, skipping", device.name)
        else:
            prompt = f"{device.name}#"
            #prompt = conn.find_prompt()
            conn.send_config_set("crypto key gen rsa mod 2048")
            conn.send_command("write mem\n\n", expect_string=prompt)
            if is_ssh_enabled(conn, device.name):
                logger.info("Enabled SSHv2 on %r", device.name)
            else:
                logger.error("Failed to enable SSHv2 on %r", device.name)

        
        # if "SSH Disabled - version 2.0" in sh_ip_ssh_output:
        #     logger.error("Router %r does not have SSH version 2 enabled", device.name)
        # elif "SSH Enabled - version 2.0" in sh_ip_ssh_output:
        #     logger.info("Router %r - SSH v2 is enabled", device.name)
        # else:
        #     logger.error("unexpected output: %s", sh_ip_ssh_output)

def main():
    lab = Lab.create()
    futures = []
    with ThreadPoolExecutor(max_workers=100) as pool:
        for device in lab.devices:
            future = pool.submit(generate_crypto_key, device)
            futures.append(future)
    for future, device in zip(futures, lab.devices):
        try:
            future.result()
        except:
            logger.error("Failed on device %r", device.name)
            
    
    
if __name__ == '__main__':
    logging.config.dictConfig(LOGGING_DICT)
    main()