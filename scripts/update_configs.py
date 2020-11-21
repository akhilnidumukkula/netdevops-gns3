import asyncio
import logging
import logging.config

from app import constants
from app.constants import LOGGING_DICT, PROJECT_ID
from app.lab import Lab
from app.gns3_project import GNS3Project

logger = logging.getLogger(__name__)


async def main():
    lab = Lab.create()
    
    gns3_project = await GNS3Project.fetch_from_id(PROJECT_ID)
    template = lab.get_template(constants.ROUTER_CONFIG_TEMPLATE)
    for device in lab.devices:
        gns3_node = gns3_project.get_node(device.name)
        node_cfg = template.render(device=device)
        await gns3_project.update_node_config(gns3_node, config=node_cfg)
        

if __name__ == '__main__':
    logging.config.dictConfig(LOGGING_DICT)
    asyncio.run(main())