import asyncio
import httpx
from httpx import Limits
import logging
import random
from copy import deepcopy
from typing import List, Dict, Any, Iterable, Tuple, ValuesView, TYPE_CHECKING, NamedTuple, Optional
from app.constants import GNS3_ROOT_API, PROJECT_ID, NUM_DEVICES_PER_ROW, NUM_DEVICES_PER_SWITCH, PIXELS_BETWEEN_DEVICES, IOS_TEMPLATE_ID, NODE_DICT, GNS3_CONTROLLER_NUM_MAX_CONN
from app.gns3_node import GNS3Node, NodeStatus
from app.gns3_link import GNS3Link, GNS3Port
from app.device import Vector
from app import utils

if TYPE_CHECKING:
    from asyncio import Semaphore 
    from app.device import Device
    from jinja2.environment import Template
    
logger = logging.getLogger(__name__)


class GNS3Project:
    def __init__(self, id: str, name_to_node: Dict[str, GNS3Node], alt_id_to_link: Dict[Tuple[Any, ...], GNS3Link]) -> None:
        self.id = id
        self.name_to_node = name_to_node
        self.alt_id_to_link = alt_id_to_link
        self.http_client = httpx.AsyncClient(
            # limits=Limits(max_keepalive_connections=25, max_connections=100)
            timeout=httpx.Timeout(read=30.0)
            )
        # self.http_client = httpx.AsyncClient()
        
        
    async def __aenter__(self) -> None:
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.http_client.aclose()
    
    @property
    def nodes(self) -> ValuesView[GNS3Node]:
        return self.name_to_node.values()
    
    @property
    def links(self) -> ValuesView[GNS3Link]:
        return self.alt_id_to_link.values()
    
    @staticmethod
    def project_api_url(project_id: str) -> str:
        return f"{GNS3_ROOT_API}/projects/{project_id}"
    
    @property
    def api_url(self) -> str:
        return GNS3Project.project_api_url(self.id)
    
    @classmethod
    async def fetch_from_id(cls, project_id: str) -> "GNS3Project":
        project_url = GNS3Project.project_api_url(project_id)
        nodes_url = f'{project_url}/nodes'
        links_url = f'{project_url}/links'
        async with httpx.AsyncClient() as http_client:
            get_nodes_task = asyncio.create_task(http_client.get(nodes_url))
            get_links_task = asyncio.create_task(http_client.get(links_url))
            await asyncio.gather(get_nodes_task, get_links_task)
            nodes_data = get_nodes_task.result().json()
            links_data = get_links_task.result().json()
            name_to_node, id_to_node = GNS3Project.parse_nodes_data(nodes_data)
            alt_id_to_link = GNS3Project.parse_links_data(links_data) #  id_to_node
            
        result = cls(id=project_id, name_to_node=name_to_node, alt_id_to_link=alt_id_to_link)
        return result  
            
    @staticmethod
    def create_http_client() -> httpx.AsyncClient:
        timeout = httpx.Timeout(read=300, pool=200)
        pool_limits = httpx.Limits(max_connections=10, max_keepalive_connections=GNS3_CONTROLLER_NUM_MAX_CONN)
        client = httpx.AsyncClient(pool_limits=pool_limits, timeout=timeout)
        return client
    
    def get_node(self, node_name: str) -> Optional[GNS3Node]:
        return self.name_to_node.get[node_name]
    
    @staticmethod
    def parse_nodes_data(data: List[Dict[str, Any]]) -> Tuple[Dict[str, GNS3Node], Dict[str, GNS3Node]]:
        name_to_node: Dict[str, GNS3Node] = {}
        id_to_node: Dict[str, GNS3Node] = {}
        for node_data in data:
            node = GNS3Node.load(node_data)
            name_to_node[node.name] = node
            id_to_node[node.id] = node
        return name_to_node, id_to_node
    
    @staticmethod
    def parse_links_data(data: List[Dict[str, Any]], 
                         # id_to_node: Dict[str, GNS3Node]
                         ) -> Dict[Tuple[Any, ...], GNS3Link]:
        alt_id_to_link: Dict[Tuple[Any, ...], GNS3Link] = {}    
        for link_data in data:
            link = GNS3Link.load(link_data) # , id_to_node
            alt_id_to_link[link.alt_id] = link
            return alt_id_to_link
        
    async def add_router_from_template(self, coordinates: Vector, hostname: str) -> GNS3Node:
        url = f"{self.api_url}/templates/{IOS_TEMPLATE_ID}"
        data = {
            "x": coordinates.x,
            "y": coordinates.y
        }
        response = await self.http_client.post(url, json=data)
        
        if 200 <= response.status_code < 300:
            logger.info("Device %r was successfully created from template", hostname)
            
            node = GNS3Node.load(response.json())
            self.name_to_node[node.name] = node
            return node
        
        else:
            logger.error("Device %r failed to create from template, error: %s", hostname, response.text)
            response.raise_for_status()

        # node_data = template_response.json()
        # node_data["name"] = device.hostname
        # node_data["label"]["text"] = device.hostname
        # node_id = node_data["node_id"]

        
    async def rename_and_move_router(self, node: GNS3Node, hostname: str, coordinates: Vector) -> GNS3Node:
        data = deepcopy(NODE_DICT)
        data["name"] = hostname
        data["label"]["text"] = hostname
        data["node_id"] = node.id
        data["x"] = coordinates.x
        data["y"] = coordinates.y

        url = f"{self.api_url}/nodes/{node.id}"
        response = await self.http_client.put(url, json=data)
        
        if response.is_error:
            logger.error("Device %r - hostname update has failed, error: %s", hostname, response.text)
            response.raise_for_status()
            
        else:
            self.name_to_node.pop(node.name, None)
            old_node_name = node.name
            node = GNS3Node.load(response.json())
            logger.info("Device %r has been renamed to %r, expected %r", old_node_name, node.name, hostname)
            self.name_to_node[node.name] = node
            return node
    
    def create_link_between_router_and_switch(self, router: GNS3Node, switch: GNS3Node, router_seq_in_group: int) -> GNS3Link:
        router_port = GNS3Port(node_id=router.id, adapter_num=0, port_num=0, node_name = router. name)
        switch_port = GNS3Port(node_id=switch.id, adapter_num=0, port_num=router_seq_in_group, node_name = switch.name)
        ports = [router_port, switch_port]
        link = GNS3Link(ports=ports)
        return link
    
    async def add_link_to_switch(self, link: GNS3Link) -> None:             
        # link = self.create_link_between_router_and_switch(router, switch, switch_port_num)
        url = f"{self.api_url}/nodes/links"
        response = await self.http_client.post(url, json=link.dump())
        if 200 <= response.status_code < 300:
            logger.info("Link %s has been added", link)
            
            res_link = GNS3Link.load(response.json())
            self.alt_id_to_link[res_link.alt_id] = res_link
            return
        
        else:
            logger.error("Link %s was not added, encountered error: %s", link, response.text)
            response.raise_for_status()
    
    async def update_node_config(self, node: GNS3Node, config: str) -> None:
        url = f"{self.api_url}/nodes/{node.id}/files/startup-config.cfg"
        response = await self.http_client.post(url, data=config)
        
        if 200 <= response.status_code < 300:
            logger.info("Node %r config has been updated", node.name)
        else:
            logger.error("Node %r config update has failed, error: %s", node.name, response.text)
            response.raise_for_status()
            
    async def start_node(self, node: GNS3Node) -> None: #, timeout: Optional[float] = None
        url = f"{self.api_url}/nodes/{node.id}/start"
        response = await self.http_client.post(url)
        
        if 200 <= response.status_code < 300:
            logger.info("Node %r has started", node.name)
            # if timeout:
            #     await asyncio.sleep(timeout)
        else:
            logger.error("Node %r has failed to start, error: %s", node.name, response.text)
            response.raise_for_status()
            
                
    async def delete_node(self, node_name: Optional[str] = None, node_id: Optional[str] = None) -> None:
        if node_id:
            url = f"{self.api_url}/nodes/{node_id}"
            response = await self.http_client.delete(url)
            node_str = node_name or node_id
            if response.is_error:
                logger.error("Failed to delete a node %r", node_str)
                response.raise_for_status()
            else:
                logger.info("Node %r has been deleted", node_str)
        elif node_name:
                node = self.name_to_node[node_name]
                return await self.delete_node(node_name=node.name, node_id=node.id)
        else:
            raise ValueError("Either node name or ID should be provisioned")
        
    async def provision_router(self, device: "Device", template: "Template") -> None: 
        #, sema: "Semaphore" (Don't need semaphore as httpx is using it internally)
        #async with sema:
        router_name = device.hostname
        switch = device.find_switch(self.name_to_node)
        coordinates = device.calculate_coordinates(switch)
        router_created = False
        
        # If router is not present then add it and rename
        if router_name not in self.name_to_node:    
            temp_router = await self.add_router_from_template(coordinates, hostname=router_name)
            router = await self.rename_and_move_router(node=temp_router, hostname=router_name, coordinates=coordinates)
            router_created = True
        
        # If router is already present then retrieve the information about it?
        else:
            router = self.name_to_node[router_name]
            
        link = self.create_link_between_router_and_switch(router, switch, device.seq_num_in_group)
        
        if link.alt_id not in self.alt_id_to_link:
            await self.add_link_to_switch(link)
        else:
            logger.info("Link %s already exists", link)
        
        # If the router has already been created then, update the configuration of the router
        if router_created or utils.is_env_var("ALWAYS_UPDATE_ROUTER_CFG"):
            router_config = template.render(device=device)
            await self.update_node_config(node=router, config=router_config)
            
            # When do we want to start the node?
            # if router.status is not NodeStatus.STARTED:
            #     await self.start_node(node=router)
            #     await asyncio.sleep(random.randint(1, 15))

    async def start_all_nodes(self) -> None:
        url = f"{self.api_url}/nodes/start"
        response = await self.http_client.post(url)
        
        if 200 <= response.status_code < 300:
            logger.info("All nodes have been started")
        else:
            logger.error("Failed to start all nodes: %s", response.text)
            response.raise_for_status()
            
    async def stop_all_nodes(self) -> None:
        url = f"{self.api_url}/nodes/stop"
        response = await self.http_client.post(url)
        
        if response.is_error:
            logger.error("Failed to stop all nodes: %s", response.text)
            response.raise_for_status()
        else:
            logger.info("All nodes have been stopped")
            
    async def add_routers(self, devices: List["Device"], template: "Template") -> None:
        ## No Need for semaphore as httpx is performing it internally
        #semaphore = asyncio.BoundedSemaphore(20)
        #tasks = [asyncio.create_task(self.provision_router(device, template=template, sema=semaphore)) for device in devices]
        #await asyncio.gather(*tasks)
        
        for device in devices:
            await self.provision_router(device, template=template)
        logger.info("Finished provisioning %d devices", len(devices))

    async def delete_nodes(self, node_names: Iterable[str]) -> None:
        tasks = [asyncio.create_task(self.delete_node(node_name=node_name))
                 for node_name in node_names
                 if node_name in self.name_to_node
            ]
        await asyncio.gather(*tasks)
        
        
    async def staggered_start(self) -> None:
        semaphore = asyncio.BoundedSemaphore(25)
        start_node_with_sema = utils.with_semaphore(semaphore=semaphore, timeout=30, random_timeout=True)(self.start_node)
        tasks = []
        for node in self.nodes:
            if not node.is_started:
                task = asyncio.create_task(start_node_with_sema(node))
                tasks.append(task)
        await asyncio.gather(*tasks)
        logger.info("All nodes have been started")