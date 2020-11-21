from typing import Dict, Optional, Any, Union, ValuesView
from app.device import Device
from pathlib import Path
from ruamel.yaml import YAML
import uuid
import random
import string

class AnsibleHost:
    def __init__(self, name: str, device: Optional[Device] = None, vars: Optional[Dict[str, Any]] = None) -> None:
        self.name = name
        self.device = device
        self.host_vars = vars
        
    def dump(self) -> Dict[str, Any]:
        return {"ansible_host": self.device.mgmt_int_ip}
    
    @classmethod
    def from_device(cls, device: Device, vars: Optional[Dict[str, Any]] = None) -> "AnsibleHost":
        host_name = device.name
        host = cls(device=device, name=host_name, vars=vars)
        return host
    
    def write_vars(self, inventory_dir: str) -> None:
        path = Path(inventory_dir) / f"host_vars/{self.name}.yaml"
        yaml = YAML(typ="safe")
        yaml.default_flow_style = False
        with open(path, "w") as f:
            yaml.dump(self.host_vars, f)


class AnsibleGroup:
    def __init__(self, name: str) -> None:
        self.name = name
        self.name_to_group : Dict[str, "AnsibleGroup"] = {}
        self.name_to_host : Dict[str, AnsibleHost] = {}
        self.vars: Dict[str, Any] = {}
        
    def add_host(self, host: Union[AnsibleHost, str]) -> AnsibleHost:
        if isinstance(host, str):
            host = AnsibleHost(name=host)
        self.name_to_host[host.name] = host
        return host
        
    def add_group(self, group: Union["AnsibleGroup", str]) -> "AnsibleGroup":
        if isinstance(group, str):
            group = AnsibleHost(group)
        self.name_to_group[group.name] = group
        return group
    
    def add_vars(self, data: Dict[str, Any]) -> None:
        self.vars.update(data)
        
    def __contains__(self, item: Any) -> bool:
        if isinstance(item, AnsibleGroup):
            return item.name in self.name_to_group
        elif isinstance(item, AnsibleHost):
            return item.name in self.name_to_host
        
    @property
    def groups(self) -> ValuesView["AnsibleGroup"]:
        return self.name_to_group.values()
    
    @property
    def hosts(self) -> ValuesView[AnsibleHost]:
        return self.name_to_host.values()
    
    def dump(self) -> Dict[str, Any]:
        hosts_data = {
            host.name: host.dump() for host in self.hosts
        }
        
        groups_data = {
            group.name: group.dump() for group in self.groups
        }
        
        result = {}
        if hosts_data:
            result["hosts"] = hosts_data
        if groups_data:
            result["children"] = groups_data
        if self.vars:
            result["vars"] = self.vars

        return result
        
class AnsibleInventory:
    def __init__(self):
        self.name_to_group: Dict[str, "AnsibleGroup"] = {}
        self.name_to_host: Dict[str, AnsibleHost] = {}
        self.add_group('all')
        
    def add_host(self, host: Union[AnsibleHost, str]) -> AnsibleHost:
        if isinstance(host, str):
            host = AnsibleHost(name=host)
        self.name_to_host[host.name] = host
        return host
        
    def add_group(self, group: Union[AnsibleGroup, str]) -> AnsibleGroup:
        if isinstance(group, str):
            group = AnsibleHost(group)
        self.name_to_group[group.name] = group
        return group
    
    def get_group(self, group_name: str) -> Optional[AnsibleGroup]:
        return self.name_to_group.get(group_name)
    
    def __contains__(self, item: Any) -> bool:
        if isinstance(item, AnsibleGroup):
            return item.name in self.name_to_group
        elif isinstance(item, AnsibleHost):
            return item.name in self.name_to_host
    
    @property
    def root(self) -> AnsibleGroup:
        return self.name_to_group['all']
    
    def write_to_dir(self, dir_path: str) -> None:
        hosts = {"all": self.root.dump()}
        path = Path(dir_path) / "hosts.yaml"
        yaml = YAML()
        yaml.default_flow_style = False
        with open(path, 'w') as f:
            yaml.dump(hosts, f)
