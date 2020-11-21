from typing import Dict, ValuesView

from app.device import Device
from jinja2 import PackageLoader, Environment, Template
from app.ansible import AnsibleGroup, AnsibleHost, AnsibleInventory
from app.constants import ANSIBLE_GLOBAL_VARS, NORNIR_DEFAULT_VARS
from app.nornir import NornirInventory, NornirHost, NornirGroup, NornirDefaults
from app.utils import create_random_data
from ruamel.yaml import YAML
from pathlib import Path


yaml = YAML(typ="safe")
yaml.default_flow_style = False

class Lab:
    def __init__(self, name_to_device: Dict[str, Device]) -> None:
        self.name_to_device = name_to_device
        
    def get_device(self, device_name: str) -> Device:
        return self.name_to_device.get(device_name)
    
    @property
    def devices(self) -> ValuesView[Device]:
        return self.name_to_device.values()

    @classmethod
    def create(cls) -> "Lab":
        name_to_device = Device.create_devices()
        lab = cls(name_to_device=name_to_device)
        return lab
    
    @property
    def jinja_env(self) -> Environment:
        return Environment(loader=PackageLoader('app', 'templates'))
    
    def get_template(self, template_path: str) -> Template:
        return self.jinja_env.get_template(template_path)
    
    def build_ansible_inventories(self, dir_path: str, random_data: bool = False) -> None:
        inventory = AnsibleInventory()
        inventory.root.add_vars(ANSIBLE_GLOBAL_VARS)
        if random_data:
            host_vars = create_random_data()
        else:
            host_vars = None
        for device in self.devices:
            ansible_host = AnsibleHost.from_device(device=device, vars=host_vars)
            
            core_router_name = device.connected_core_router_name
            core_router_group = inventory.get_group(core_router_name)
            if core_router_group is None:
                core_router_group = inventory.add_group(core_router_name)
            if core_router_group not in inventory.root:
                inventory.root.add_group(core_router_group)
            # core_router_group.add_host(ansible_host)
            
            conn_switch_name = device.connected_switch_name
            switch_group = inventory.get_group(conn_switch_name)
            if switch_group is None:
                switch_group = inventory.add_group(conn_switch_name)
            if switch_group not in core_router_group:
                core_router_group.add_group(switch_group)
            switch_group.add_host(ansible_host)
            if ansible_host.host_vars:
                ansible_host.write_vars(inventory_dir=dir_path)
                
        inventory.write_to_dir(dir_path)

    def build_nornir_inventory(self, dir_path: str, host_data_separate: bool = True) -> None:
        inventory = NornirInventory(defaults=NornirDefaults(**NORNIR_DEFAULT_VARS))
        random_data = create_random_data()
        dir_path = Path(dir_path)
        for device in self.devices:
            nr_host = NornirHost(
                name=device.name,
                hostname=device.mgmt_int_ip,
                groups=[device.connected_switch_name]
            )
            inventory.add_host(nr_host)
            
            if not inventory.contains_group(device.connected_core_router_name):
                nr_group = NornirGroup(
                    name=device.connected_core_router_name
                )
                inventory.add_group(nr_group)
                
            if not inventory.contains_group(device.connected_switch_name):
                nr_group = NornirGroup(
                    name=device.connected_switch_name,
                    groups=[device.connected_core_router_name]
                )
                inventory.add_group(nr_group)
                
                with open(dir_path / f"host_vars/{device.name}.yaml", "w") as f:
                    yaml.dump(random_data, f)
                
            inventory.write_to_dir(dir_path="nornir/inventory")