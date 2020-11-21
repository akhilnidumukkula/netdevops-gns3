import logging.config
from typing import List

from nornir import InitNornir
from nornir.core.filter import F
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.tasks.data import load_yaml

from constants import LOGGING_DICT

COMMANDS = ["show version", "show ip int br", "show memory statistics", "show arp", "show ip route", "show interfaces"]

def gather_commands(task, commands: List[str], load_data: bool = False) -> None:
    if load_data:
        task.run(task=load_yaml, file=f"inventory/host_vars/{task.host.name}.yaml")
    with open(f"output/{task.host.name}.txt", "w") as f:
        prompt = f"{task.host.name}#"
        for command in commands:
            result = task.run(task=netmiko_send_command, command_string=command, expect_string=prompt)
            f.write(f"==={command}===\n{result.result}\n\n")

def main():
    logging.config.dictConfig(LOGGING_DICT)
    with InitNornir(config_file="config.yaml") as nr:
        nr = InitNornir(config_file="config.yaml")
        #nr_sw1 = nr.filter(F(has_parent_group="Switch1"))
        #nr_sw1.run(task=gather_commands, commands=COMMANDS)
        nr.run(task=gather_commands, commands=COMMANDS, load_data=True)
    
if __name__ == '__main__':
    main()