from ipaddress import IPv4Address, ip_address, IPv4Interface, ip_interface, IPv4Network
from typing import Optional, TYPE_CHECKING, Dict, Tuple, NamedTuple
from app import utils
from app.constants import NUM_DEVICES_PER_SWITCH, NUM_SWITCHES_PER_CORE_ROUTER, NUM_DEVICES_PER_ROW, PIXELS_BETWEEN_DEVICES, START_ROUTER_NUM, END_ROUTER_NUM

MGMT_IP_TEMPLATE = "10.15.{group}.{num}/24"

if TYPE_CHECKING:
    from app.gns3_node import GNS3Node
    
    
class Vector(NamedTuple):
    x: int
    y: int
    
class Device:
    def __init__(
        self, 
        num: int, 
        mgmt_int: IPv4Interface, 
        host: Optional[str] = None, 
        hostname: Optional[str] = None
        ) -> None:
        
        self.num = num
        self.mgmt_int = mgmt_int
        self._host = host
        self._hostname = hostname
        self.gns3_node = None

    def __repr__(self) -> str:
        return utils.create_repr(self, ("hostname", "mgmt_int"))
    
    @property
    def host(self) -> str:
        if self._host: 
            return self._host
        else:
            return self.mgmt_int_ip
        
    @property
    def hostname(self) -> str:
        if self._hostname: 
            return self._hostname
        else:
            return self.name
        
    @property
    def name(self) -> str:
        return f"{self.num}"
        
    @property
    def group_num(self) -> int:
        # Group number from 1 to 10
        return (self.num -1) // NUM_DEVICES_PER_SWITCH + 1
    
    @property
    def connected_switch_name(self) -> str:
        return f"Switch{self.group_num}"
    
    @property
    def connected_core_router_name(self) -> str:
        core_router_num = (self.group_num - 1) // NUM_SWITCHES_PER_CORE_ROUTER + 1
        return f"CORE{core_router_num }"

    @classmethod
    def from_sequence_num(cls, num: int) -> "Device":
        group_num = (num-1) // NUM_DEVICES_PER_SWITCH + 1
        num_in_group = (num-1) % NUM_DEVICES_PER_SWITCH + 1
        mgmt_int = ip_interface(MGMT_IP_TEMPLATE.format(group = group_num, num = num_in_group))
        device = cls(num=num, mgmt_int=mgmt_int)
        return device
  
    @property
    def mgmt_int_ip(self) -> str:
        return str(self.mgmt_int.ip)
    
    @property
    def mgmt_int_net(self) -> IPv4Network:
        return self.mgmt_int.network

    @property
    def default_gw_ip(self) -> str:
        result = str(list(self.mgmt_int_net.hosts())[-1])
        return result

    @ property
    def mgmt_int_network_addr(self) -> str:
        result = str(self.mgmt_int_net.network_address)
        return result

    @ property
    def mgmt_int_mask(self) -> str:
        result = str(self.mgmt_int_net.netmask)
        return result

    def calculate_coordinates(self, switch: "GNS3Node") -> Vector:
        seq_num_in_group = (self.num - 1) % NUM_DEVICES_PER_SWITCH # 0 .. 99
        row_number = seq_num_in_group // NUM_DEVICES_PER_ROW # 0 .. 3
        pos_within_row = seq_num_in_group % 25 # 0 .. 24
        
        rel_pos_within_row = pos_within_row - NUM_DEVICES_PER_ROW // 2
        num_rows = NUM_DEVICES_PER_SWITCH // NUM_DEVICES_PER_ROW
        router_x = switch.x + PIXELS_BETWEEN_DEVICES * rel_pos_within_row
        router_y = switch.y - (num_rows - row_number) * PIXELS_BETWEEN_DEVICES
        vector = Vector(router_x, router_y)
        return vector
    
    def find_switch(self, name_to_node: Dict[str, "GNS3Node"]) -> "GNS3Node":
        switch_name = f"Switch{self.group_num}"
        switch = name_to_node[switch_name]
        return switch
    
    @property
    def seq_num_in_group(self) -> int:
        """1..NUM_DEVICES_PER_SWITCH"""
        return (self.num - 1) % NUM_DEVICES_PER_SWITCH + 1
    
    @classmethod
    def create_devices(cls) -> Dict[str, "Device"]:
        name_to_device : Dict[str, "Device"] = {}
        for i in range(START_ROUTER_NUM, END_ROUTER_NUM + 1):
            device = cls.from_sequence_num(i)
            name_to_device[device.name] = device
        return name_to_device