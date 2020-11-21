from ruamel.yaml import YAML
from typing import Dict, Optional, Any, List
from pathlib import Path


yaml = YAML(typ="safe")
yaml.default_flow_style = False

class NornirData:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data
        
    def save_on_disk(self, path: str) -> None:
        with open(path, 'w') as f:
            yaml.dump(self.data, f)

class InventoryElement:
    def __init__(self, name: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None, hostname: Optional[str] = None, platform: Optional[str] = None, groups: Optional[List[str]] = None, data: Optional[NornirData] = None) -> None:
        self.name = name
        self.username = username
        self.password = password
        self.hostname = hostname
        self.platform = platform
        self.groups = groups
        self.data = data
        
    def dump(self) -> Dict[str, Any]:
        data = {}
        if self.hostname:
            data['hostname'] = self.hostname
        if self.username:
            data['username'] = self.username
        if self.password:
            data['password'] = self.password
        if self.platform:
            data['platform'] = self.platform
        if self.groups:
            data['groups'] = self.groups
        if self.data:
            data['data'] = self.data
        
        return data

class NornirHost(InventoryElement):
    pass

class NornirGroup(InventoryElement):
    pass

class NornirDefaults(InventoryElement):
    pass

class NornirInventory:

    def __init__(self, hosts: Optional[Dict[str, NornirHost]] = None, groups: Optional[Dict[str, NornirGroup]] = None, defaults: Optional[NornirDefaults] = None) -> None:
        if hosts is None:
            hosts = {}
        self.hosts = hosts
        if groups is None:
            groups = {}
        self.groups = groups
        self.defaults = defaults
        
    def add_host(self, host: NornirHost) -> None:
        self.hosts[host.name] = host
        
    def get_group(self, group_name: str) -> NornirGroup:
        return self.groups[group_name]
        
    def add_group(self, group: NornirGroup) -> None:
        self.groups[group.name] = group
        
    def contains_group(self, group_name: str) -> bool:
        return group_name in self.groups
        
    def write_to_dir(self, dir_path: str) -> None:
        dir_path = Path(dir_path)
        if self.hosts:
            hosts_data = {
                host.name: host.dump() for host in self.hosts.values()
            }
            hosts_file_path = dir_path / "hosts.yaml"
            with open(hosts_file_path, 'w') as f:
                yaml.dump(hosts_data, f)
        if self.groups:
            groups_data = {
                group.name: group.dump() for group in self.groups.values()
            }
            groups_file_path = dir_path / "groups.yaml"
            with open(groups_file_path, 'w') as f:
                yaml.dump(groups_data, f)
        if self.defaults:
            defaults_data = self.defaults.dump()
            default_file_path = dir_path / "default.yaml"
            with open(default_file_path, 'w') as f:
                yaml.dump(defaults_data, f)
