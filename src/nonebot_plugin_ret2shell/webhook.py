import json
from nonebot import logger, get_driver
from nonebot.drivers import URL, Request, Response, ASGIMixin, HTTPServerSetup
from .report import send_admin_msg
from .config import config


async def response_json(json_data: dict, status_code: int = 200):
    return Response(
        status_code=status_code,
        headers={"Content-Type": "application/json"},
        content=json.dumps(json_data)
    )


async def webhook(request: Request):
    if request.headers.get("X-Plugin-Name") != config.client_label:
        return await response_json({"success": False}, status_code=403)
    try:
        data = request.json
        logger.opt(colors=True).debug(f'🪝 <m>Webhook</m> | {data}')
        event = data.get('event')
        user_nickname = data.get('user').get('nickname')
        challenge_name = data.get('challenge').get('name')
        stop_reason = data.get('stop_reason')
    except Exception as e:
        logger.exception("❌ Caught exception: ")
        return await response_json({"success": False}, status_code=400)

    message: str = ""
    if event == "start":
        message = f"""🟢 选手 [{user_nickname}] 启动了题目 [{challenge_name}] 的在线环境。"""
    elif event == "delay":
        message = f"""⏰ 选手 [{user_nickname}] 将题目 [{challenge_name}] 的在线环境延长了一小时。"""
    elif event == "stop":
        if stop_reason == "manual":
            message = f"""🛑 选手 [{user_nickname}] 手动停止了题目 [{challenge_name}] 的在线环境。"""
        elif stop_reason == "timeout":
            message = f"""🛑 选手 [{user_nickname}] 题目 [{challenge_name}] 的在线环境因超时而自动停止。"""

    await send_admin_msg(message)
    return await response_json({"success": True})


webhook_server_mounted: bool = False
driver = get_driver()
@driver.on_bot_connect
async def run_webhook_server():
    global webhook_server_mounted
    if not webhook_server_mounted:
        # Setup Webhook Route
        if isinstance(driver, ASGIMixin):
            driver.setup_http_server(
                HTTPServerSetup(
                    path=URL(config.webhook_route),
                    method="POST",
                    name="webhook",
                    handle_func=webhook,
                )
            )
        logger.opt(colors=True).success(f'✅ Webhook server mounted at "<y>{config.webhook_route}</y>"')
        webhook_server_mounted = True

