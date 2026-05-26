import asyncio

import nonebot
from websockets.asyncio.client import connect
from nonebot import logger, get_driver
from .events import Event, from_json
from .report import send_event_msg
from .config import config


async def ws_client():
    """
    带有自动重连机制的 WebSocket 客户端
    """
    ws_uri = f"{config.ret2shell_ws_link}&client={config.client_label}"
    max_count = 8  # 最大翻倍次数
    retry_count = 0
    base_delay = 1  # 初始重连延迟（秒）

    while True:
        try:
            # 尝试建立连接
            async with connect(ws_uri) as websocket:
                logger.info(f"✅ Connected to event pushing API: {ws_uri}")
                retry_count = 0  # 连接成功，重置计数器

                # 持续监听并处理消息
                async for message in websocket:
                    logger.debug(f"📨 Received via WebSocket: {message}")
                    event = from_json(message, Event)
                    await send_event_msg(event)

        # 捕获连接关闭或其他网络异常
        except Exception as e:
            logger.error(e)
            retry_count += 1
            delay = base_delay
            if retry_count < max_count:
                # 计算延迟时间，使用指数退避策略
                # 例如: 1s, 2s, 4s, 8s...
                delay = base_delay * (2 ** (retry_count - 1))
            logger.warning(f"⚠️ Connection lost. Reconnecting in {delay}s... (Attempt {retry_count})")
            await asyncio.sleep(delay)


# Handle our WebSocket client according to bot connection
driver = get_driver()
ws_client_task: asyncio.Task = None
logger.info(f"✅ Plugin loaded. Waiting for bot connection...")


@driver.on_bot_connect
async def run_ws_client():
    if len(nonebot.get_bots()) == 1:
        global ws_client_task
        logger.info(f"✅ Bot connected. Trying to connect to event pushing API...")
        if ws_client_task is None:
            ws_client_task = asyncio.create_task(ws_client())


@driver.on_bot_disconnect
async def shutdown_ws_client():
    if len(nonebot.get_bots()) == 0:
        global ws_client_task
        logger.warning("⚠️ There are no bots connected. Closing connection to event pushing API...")
        if ws_client_task and not ws_client_task.done():
            ws_client_task.cancel()
            # 等待任务实际结束
            try:
                await ws_client_task
            except asyncio.CancelledError:
                pass
        # 确认任务彻底结束后，再清空引用
        ws_client_task = None

