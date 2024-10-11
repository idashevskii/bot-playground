import asyncio


async def event_wait_timeout(evt: asyncio.Event, timeout: float):
    try:
        await asyncio.wait_for(evt.wait(), timeout)
    except asyncio.TimeoutError:
        ...
