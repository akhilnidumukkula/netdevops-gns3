import asyncio
import logging
import logging.config
from typing import TYPE_CHECKING

from app.constants import LOGGING_DICT, PROJECT_ID
from app.gns3_project import GNS3Project

if TYPE_CHECKING:
    from jinja2.environment import Template
    
logger = logging.getLogger(__name__)

async def main():
    gns3_project = await GNS3Project.fetch_from_id(PROJECT_ID)
    #await gns3_project.start_all_nodes()
    await gns3_project.staggered_start()
    
if __name__ == '__main__':
    logging.config.dictConfig(LOGGING_DICT)
    asyncio.run(main())