import asyncio
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qsl
import hashlib
import httpx
from nonebot import logger
from .config import config
from .__version__ import __version__

client: httpx.AsyncClient
api_base_url: str
game_id: str
token: str = "not_logged_in"


async def init_http_api():
    ws_link = config.ret2shell_ws_link
    urlparsed = urlparse(ws_link)
    scheme = urlparsed.scheme
    socket = urlparsed.netloc

    global api_base_url, game_id, client
    api_base_url = f'{"https" if scheme == "wss" else "http"}://{socket}/api'
    client = httpx.AsyncClient(base_url=api_base_url, headers={"User-Agent": f"python-httpx/{httpx.__version__} {config.client_label}/{__version__}"})
    game_id = dict(parse_qsl(urlparsed.query)).get("game_id")

    logger.opt(colors=True).info(f'🎯 Using HTTP API base URL: "<y>{api_base_url}</y>", game id: <y>{game_id}</y>')


async def solve_pow(criteria: str) -> str:
    """
    异步版本的 PoW 计算（通过定期让出控制权避免阻塞事件循环）。

    参数:
        criteria: 字符串，格式为 "difficulty#challenge"，例如 "3#abc"

    返回:
        找到的答案字符串，格式为 challenge + nonce_hex
    """
    difficulty_str, challenge = criteria.split('#', 1)
    difficulty = int(difficulty_str)
    target_prefix = '0' * difficulty

    nonce = 0
    while True:
        nonce += 1
        nonce_hex = f"{nonce:x}"
        data = f"{challenge}{nonce_hex}".encode('utf-8')
        hash_hex = hashlib.sha256(data).hexdigest()

        if hash_hex.startswith(target_prefix):
            return f"{challenge}{nonce_hex}"

        # 每计算 1000 次让出一次控制权，可调整频率
        if nonce % 1000 == 0:
            await asyncio.sleep(0)


async def login():
    captcha_response = await client.get("/account/captcha")
    captcha_data = captcha_response.json()
    captcha_id = captcha_data.get("id")
    captcha_challenge = captcha_data.get("challenge")

    captcha_answer = await solve_pow(captcha_challenge)

    login_json = {
        "account": config.ret2shell_account,
        "password": config.ret2shell_password,
        "captcha_id": captcha_id,
        "captcha_answer": captcha_answer
    }
    login_response = await client.post("/account/login", json=login_json)
    if login_response.status_code == 200:
        global token
        token = login_response.headers.get("Set-Token")
    elif login_response.status_code == 403:
        logger.error("❌ Account verification failed! Falling back to less detailed mode from the next event on.")
        config.ret2shell_account = None
        config.ret2shell_password = None
        return


async def get_api_json(api_entry_uri: str, headers: dict = None, **kwargs):
    final_headers = {"Authorization": f"Bearer {token}", **(headers or {})}
    response = await client.get(api_entry_uri, headers=final_headers, **kwargs)

    if response.status_code == 200:
        data = response.json()
        logger.opt(colors=True).debug(f'🌐 <m>HTTP</m> <y>{api_entry_uri}</y> | {data}')
        return data
    elif response.status_code == 401:
        if not config.ret2shell_account or not config.ret2shell_password:
            return None
        logger.opt(colors=True).info(f'🌐 <m>HTTP</m> <y>{api_entry_uri}</y> | 🔑 Token expired, re-logging in...')
        await login()
        return await get_api_json(api_entry_uri, headers, **kwargs)
    return None


async def get_game_timestamp():
    data = await get_api_json(f"/game/{game_id}")

    if data is None:
        logger.critical("❌ Game not found, is it hidden?")
        return 0, 0
    else:
        start_at = data.get("start_at")
        end_at = data.get("end_at")
        return start_at, end_at


async def get_game_info():
    data = await get_api_json(f"/game/{game_id}")

    name = data.get("name")
    brief = data.get("brief")
    start_at = data.get("start_at")
    end_at = data.get("end_at")
    return f"""🎯 赛事: {name}\n简介: {brief}\n时间: {time.strftime("%Y/%m/%d %H:%M", time.localtime(start_at))} - {time.strftime("%Y/%m/%d %H:%M", time.localtime(end_at))}\n链接: {str(client.base_url).replace("/api/", "")}/games/{game_id}"""


async def get_scoreboard(show_non_positive: bool = False):
    params = {
        'page': '1',
        'page_size': '10',
        'order': 'score',
        'asc': 'false',
        'min_state': '3',
    }
    data = await get_api_json(f"/game/{game_id}/team", params=params)

    teams = data[0]
    message: str = "🏆 积分板"
    for index, (team) in enumerate(teams, start=1):
        if index == 1:
            index = "🥇"
        elif index == 2:
            index = "🥈"
        elif index == 3:
            index = "🥉"
        else:
            index = f" {index}. "

        team_name = team.get("name")
        team_score = team.get("score")

        if team_score <= 0 and not show_non_positive:
            continue
        else:
            message += f"""\n{index} [{team_name}] {team_score} pts"""
    message += f"""\n更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    return message


async def get_challenge_info(challenge_id: int):
    data = await get_api_json(f"/game/{game_id}/challenge/{challenge_id}")

    if data is None:
        return """❔ 找不到该题目。"""
    elif data.get("hidden"):
        return """🏳️ 该题目未公开。"""
    else:
        name = data.get("name")
        tag_name = data.get("tag")[0].get("name")
        score = data.get("score")
        submit_data = await get_api_json(f"/game/{game_id}/challenge/{challenge_id}/submit")
        solves = submit_data.get("solves")
    return f"""🚩 题目: [{name}]\n方向: [{tag_name}]\n当前分数: {score} pts\n已解出数: {solves}"""


async def get_team_info(team_id: int):
    data = await get_api_json(f"/game/{game_id}/team/{team_id}")

    if data is None:
        return """❔ 找不到该队伍。"""
    else:
        name = data.get("name")
        tag = data.get("tag")
        score = data.get("score")
        rank_data = await get_api_json(f"/game/{game_id}/team/{team_id}/rank")
        rank = rank_data
        return f"""🧑‍🤝‍🧑 队伍: [{name}]\n{"" if tag is None else f"标签: {tag}\n"}当前分数: {score} pts\n当前排名: {rank}"""


async def get_hint_details(challenge_id: int):
    data = await get_api_json(f"/game/{game_id}/challenge/{challenge_id}/hint")

    latest_hint = data[-1]
    hint_cost = latest_hint.get("cost")
    hint_content = latest_hint.get("content")
    hint_created_at = latest_hint.get("created_at")
    return hint_cost, hint_content, hint_created_at


async def get_notification_details(title: str):
    data = await get_api_json(f"/game/{game_id}/notification/")

    for notification in data:
        if notification.get("title") == title:
            content = notification.get("content")
            published_at = notification.get("published_at")
            return content, published_at
    return None, 0

