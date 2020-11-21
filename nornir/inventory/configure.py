import logging.config
from typing import List

from nornir import InitNornir
from nornir.core.filter import F
from nornir_netmiko.tasks import netmiko_send_config
from nornir_utils.plugins.tasks.data import load_yaml
from nornir_jinja2.plugins.tasks import template_file

from constants import LOGGING_DICT


#COMMANDS = ["show version", "show ip int br", "show memory statistics", "show arp", "show ip route", "show interfaces"]

def configure(task, load_data: bool = False) -> None:
    if load_data:
        data = task.run(task=load_yaml, file=f"inventory/host_vars/{task.host.name}.yaml").result
        random_data = data['random'][0]
    else:
        random_data = None
    
    config = task.run(task=template_file, template='config.j2', path='templates', random_data=random_data).result #host=task.host
    task.run(task=netmiko_send_config, config_commands= config, exit_config_mode=False, delay_factor=2)


def main():
    logging.config.dictConfig(LOGGING_DICT)
    with InitNornir(config_file="config.yaml") as nr:
        nr = InitNornir(config_file="config.yaml")
        #nr_sw1 = nr.filter(F(has_parent_group="Switch1"))
        #nr_sw1.run(task=gather_commands, commands=COMMANDS)
        nr.run(task=configure, load_data=False)
    
if __name__ == '__main__':
    main()