import asyncio

from websockets.asyncio.client import connect
from nonebot import logger, get_driver, get_plugin_config
from .events import Event, from_json
from .send import send_event_msg
from .config import Config

config = get_plugin_config(Config)
client_label = f"nonebot-plugin-ret2shell"
ws_uri = f"{config.ret2shell_ws_link}&client={client_label}"


async def ws_client():
    """
    带有自动重连机制的 WebSocket 客户端
    """
    max_count = 8  # 最大翻倍次数
    retry_count = 0
    base_delay = 1  # 初始重连延迟（秒）

    while True:
        try:
            # 尝试建立连接
            async with connect(ws_uri) as websocket:
                logger.info(f"✅ Connected to event pushing API: {config.ret2shell_ws_link}")
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
            if retry_count < max_count:
                # 计算延迟时间，使用指数退避策略
                # 例如: 1s, 2s, 4s, 8s...
                delay = base_delay * (2 ** (retry_count - 1))
            logger.warning(f"⚠️ Connection lost. Reconnecting in {delay}s... (Attempt {retry_count})")
            await asyncio.sleep(delay)


# If we run our WebSocket client directly using the code below,
# NoneBot's Uvicorn server will be broken.
# asyncio.run(ws_client())

# So we have to run our WebSocket client inside NoneBot's loop
driver = get_driver()
logger.info(f"✅ Plugin loaded. Waiting for bot connection...")


@driver.on_bot_connect
async def run_ws_client():
    asyncio.get_running_loop().create_task(ws_client())

