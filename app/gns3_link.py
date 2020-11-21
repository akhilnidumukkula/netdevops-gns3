from typing import Dict, Any, List, TYPE_CHECKING, NamedTuple, Tuple, Optional
import attr
from app import utils

if TYPE_CHECKING:
    from app.gns3_node import GNS3Node
    
class GNS3Port(NamedTuple):
    node_id: str
    adapter_num: int
    port_num: int
    node_name: Optional[str] = None
    
    def dump(self) -> Dict[str, Any]:
        return {
            "adapter_number": self.adapter_num,
            "port_number": self.port_num,
            "node_id": self.node_id
        }


@attr.s(auto_attribs=True, kw_only=True)
class GNS3Link:
    id: Optional[str] = None
    type: str = "ethernet"
    ports: List["GNS3Port"]
    
    @property
    def alt_id(self) -> Tuple[Any, ...]:
        sorted_ports = sorted(self.ports)
        first_port = sorted_ports[0]
        second_port = sorted_ports[1]
        return (first_port.node_id, first_port.adapter_num, first_port.port_num, second_port.node_id, second_port.adapter_num, second_port.port_num)

    @classmethod
    def load(cls, data: Dict[str, Any], 
            # id_to_node: Dict[str, "GNS3Node"]
             ) -> "GNS3Link":
        ports = [
            GNS3Port(adapter_num=port_conn_data["adapter_number"], port_num=port_conn_data["port_number"], node_id=port_conn_data["node_id"])
            for port_conn_data in data["nodes"]
        ]
        link_data = {
            "id": data["link_id"],
            # "type": data["link_type"],
            "ports": ports
        }
        result = cls(**link_data)
        return result
    
    @property
    def first_port(self) -> GNS3Port:
        return self.ports[0]
    
    @property
    def second_port(self) -> GNS3Port:
        return self.ports[1]
    
    def dump(self) -> Dict[str, Any]:
        data = {
            "link_id": self.id,
            "link_type": self.type,
            "nodes": [port.dump() for port in self.ports]
        }
        result = utils.filter_none(data)
        return result
    
    def __str__(self) -> str:
        sorted_ports = sorted(self.ports)
        first_port = sorted_ports[0]
        second_port = sorted_ports[1]
        result = (
            f"{first_port.node_name}:"
            f"{first_port.adapter_num}/{first_port.port_num} <-> "
            f"{second_port.node_name}:"
            f"{second_port.adapter_num}/{second_port.port_num}"
            )
        return result
