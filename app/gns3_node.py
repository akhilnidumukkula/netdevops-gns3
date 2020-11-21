from enum import Enum
from typing import Dict, Any
import attr

class NodeStatus(Enum):
    STARTED = "started"
    STOPPED = "stopped"
    SUSPENDED = "suspeneded"

@attr.s(auto_attribs=True, kw_only=True, frozen=True)
class GNS3Node:
    id: str
    type: str
    name: str
    x: int
    y: int
    z: int
    status: NodeStatus

    @classmethod
    def load(cls, data: Dict[str, Any]) -> "GNS3Node":
        node_data = {
            "id": data["node_id"],
            "type": data["node_type"],
            "name": data["name"],
            "x": data["x"],
            "y": data["y"],
            "z": data["z"],
            "status": NodeStatus(data["status"])
        }
        result = cls(**node_data)
        return result

    @property
    def is_started(self) -> bool:
        return self.status is NodeStatus.STARTED