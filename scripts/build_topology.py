import asyncio
import aiofiles
from itertools import groupby
from operator import attrgetter
import logging
import logging.config
from ipaddress import IPv4Network
from jinja2 import Environment, PackageLoader
from app.gns3_project import GNS3Project
from app.device import Device
from app.constants import START_ROUTER_NUM, END_ROUTER_NUM, PROJECT_ID, LOGGING_DICT, ROUTER_CONFIG_TEMPLATE
from typing import List, Tuple, TYPE_CHECKING

logger = logging.getLogger(__name__)

async def main():
    jinja_env = Environment(
        loader=PackageLoader('app', 'templates')
    )
    devices = [Device.from_sequence_num(i) for i in range (START_ROUTER_NUM, END_ROUTER_NUM + 1)]   

    # dhcp_template = jinja_env.get_template(DHCP_CONFIG_TEMPLATE)
    # await generate_dhcp_config(devices, template=dhcp_template)
    
    router_config_template = jinja_env.get_template(ROUTER_CONFIG_TEMPLATE)
    gns3_project = await GNS3Project.fetch_from_id(PROJECT_ID)
    
    await gns3_project.add_routers(devices=devices, template=router_config_template)
        
if __name__ == "__main__":
    logging.config.dictConfig(LOGGING_DICT)
    asyncio.run(main())
