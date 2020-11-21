import asyncio
import aiofiles
import uvloop
import netdev
import netdev.exceptions

from app.lab import Lab
from app import utils
from app import constants

COMMANDS = ['show version', 'show ip int br', 'show memory statistics', 'show arp', 'show ip route', 'show interfaces']

async def _gather_commands(device, params) -> None:
    async with netdev.create(**params) as conn:
        async with aiofiles.open(f"output/routers/{device.name}.txt", 'w') as f:
            for command in COMMANDS:
                output = await conn.send_command(command)
                await f.write(f"=== {command} ===\n{output}\n\n")


async def gather_commands(device) -> None:
    params = {
        'username': constants.DEVICE_USERNAME,
        'password': constants.DEVICE_PASSWORD,
        'device_type': 'cisco_ios',
        'host': device.mgmt_int_ip,
        'timeout': 90
    }
    try:
        await _gather_commands(device, params)
    except netdev.exceptions.TimeoutError:
        await _gather_commands(device, params)


async def main():
    lab = Lab.create()
    devices = list(lab.devices)
    sema = asyncio.BoundedSemaphore(100)
    gather_commands_with_sema = utils.with_semaphore(sema)(gather_commands)
    tasks = [
        asyncio.create_task(gather_commands_with_sema(device))
        for device in devices
    ]
    await asyncio.gather(*tasks)
    
if __name__ == '__main__':
    uvloop.install()
    asyncio.run(main())
