import asyncio
import logging
import logging.config
from app.constants import LOGGING_DICT, START_ROUTER_NUM, END_ROUTER_NUM, PROJECT_ID

from app.device import Device
from app.gns3_project import GNS3Project

logger = logging.getLogger(__name__)


async def main():
    # devices = [Device.from_sequence_num(i) for i in range (START_ROUTER_NUM, END_ROUTER_NUM + 1)]
    gns3_project = await GNS3Project.fetch_from_id(PROJECT_ID)
    switch_ids = {node.id for node in gns3_project.nodes if node.name.startswith('Switch')}
    # await gns3_project.delete_nodes(device.hostname for device in devices)
    for link in gns3_project.links:
        if link.first_port.node_id in switch_ids and link.first_port.port_num != 0:
            node_id = link.second_port.node_id
            await gns3_project.delete_node(node_id=node_id)
        elif link.second_port.node_id in switch_ids and link.second_port.port_num != 0:
            node_id = link.first_port.node_id
            await gns3_project.delete_node(node_id=node_id)
            
if __name__ == '__main__':
    logging.config.dictConfig(LOGGING_DICT)
    asyncio.run(main())
