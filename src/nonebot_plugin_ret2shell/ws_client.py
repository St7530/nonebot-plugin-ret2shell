import asyncio
import nonebot
from websockets.asyncio.client import connect
import websockets.http11
from nonebot import logger, get_driver
from .events import Event, from_json
from .report import send_event_msg, send_ops_msg
from .config import config
from .__version__ import __version__


async def ws_client():
    """
    带有自动重连机制的 WebSocket 客户端
    """
    ws_uri = f"{config.ret2shell_ws_link}&client={config.client_label}+v{__version__}"
    max_count = 7  # 最大翻倍次数
    retry_count = 0

    while True:
        try:
            # 尝试建立连接
            async with connect(ws_uri, user_agent_header=f"{websockets.http11.USER_AGENT} {config.client_label}/{__version__}") as websocket:
                logger.opt(colors=True).success(f"✅ Connected to WebSocket event API: <y>{ws_uri}</y>")
                retry_count = 0  # 连接成功，重置计数器

                # 持续监听并处理消息
                async for message in websocket:
                    logger.opt(colors=True).debug(f'📨 <m>WebSocket</m> | {message}')
                    event = from_json(message, Event)
                    await send_event_msg(event)

        # 捕获连接关闭或其他网络异常
        except Exception as e:
            logger.exception("❌ Caught exception: ")
            retry_count += 1
            delay = 60 # 最后尝试频率保持在 60s
            if retry_count < max_count:
                # 计算延迟时间，使用指数退避策略
                # 例如: 1s, 2s, 4s, 8s...
                delay = 2 ** (retry_count - 1)
            logger.warning(f"⚠️ Connection lost. Reconnecting in {delay}s... (Attempt {retry_count})")
            await send_ops_msg(f"👿 运行异常\n{e}")
            await asyncio.sleep(delay)


# Handle our WebSocket client according to bot connection
driver = get_driver()
ws_client_task: asyncio.Task = None
logger.info(f"✅ Plugin loaded. Waiting for bot connection...")


@driver.on_bot_connect
async def run_ws_client():
    if len(nonebot.get_bots()) == 1:
        global ws_client_task
        logger.info(f"✅ Bot ready. Connecting to WebSocket event API...")
        if ws_client_task is None:
            ws_client_task = asyncio.create_task(ws_client())


@driver.on_bot_disconnect
async def shutdown_ws_client():
    if len(nonebot.get_bots()) == 0:
        global ws_client_task
        logger.warning("⚠️ There are no bots connected. Closing connection to WebSocket event API...")
        if ws_client_task and not ws_client_task.done():
            ws_client_task.cancel()
            # 等待任务实际结束
            try:
                await ws_client_task
            except asyncio.exceptions.CancelledError:
                pass
        # 确认任务彻底结束后，再清空引用
        ws_client_task = None

