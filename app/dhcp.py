import asyncio
import aiofiles
import logging
import logging.config
from itertools import groupby
from operator import attrgetter
from ipaddress import IPv4Network
from app.device import Device
from jinja2 import Environment, PackageLoader
from typing import List, Tuple, TYPE_CHECKING
from app.constants import DOMAIN_NAME, DNS_SERVERS, ENS_NETWORK, ENS_NET_MASK, LOGGING_DICT, ROUTER_CONFIG_TEMPLATE, START_ROUTER_NUM, END_ROUTER_NUM

if TYPE_CHECKING:
    from jinja2.environment import Template
    
logger = logging.getLogger(__name__)

async def generate_dhcp_config(devices: List[Device], template: "Template"):
    sorted_devices = sorted(devices, key=attrgetter("mgmt_int_net"))
    networks_with_devices: List[Tuple[IPv4Network, List[Device]]] = []
    for network, _devices in groupby(sorted_devices, key=attrgetter("mgmt_int_net")):
        networks_with_devices.append((network, list(_devices)))
    

    dhcp_conf = template.render(
        domain_name=DOMAIN_NAME,
        dns_servers=DNS_SERVERS,
        ens_network = ENS_NETWORK,
        ens_net_mask = ENS_NET_MASK,
        devices=devices,
        networks_with_devices=networks_with_devices
    )
    async with aiofiles.open("output/dhcpd.conf", "w") as f:
        await f.write(dhcp_conf)
        
async def main():
    jinja_env = Environment(
        loader=PackageLoader('app', 'templates')
    )
    devices = [Device.from_sequence_num(i) for i in range (START_ROUTER_NUM, END_ROUTER_NUM + 1)]   

    dhcp_template = jinja_env.get_template(ROUTER_CONFIG_TEMPLATE)
    await generate_dhcp_config(devices, template=dhcp_template)


if __name__ == '__main__':
    logging.config.dictConfig(LOGGING_DICT)
    asyncio.run(main())