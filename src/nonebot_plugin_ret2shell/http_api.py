from datetime import datetime
import time

import httpx
import asyncio
from urllib.parse import urlparse, parse_qsl
from nonebot import logger
from .config import config

params = dict(parse_qsl(urlparse(config.ret2shell_ws_link).query))
socket = urlparse(config.ret2shell_ws_link).netloc
game_id = params.get("game_id")
api_base_url = f"https://{socket}/api"


# Try HTTPS
async def try_https():
    logger.info(f" Validating if {socket} supports HTTPS...")
    global api_base_url
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{api_base_url}/platform/info", headers={"User-Agent": config.client_label})
            logger.info(f"✅ {socket} supports HTTPS.")
    except httpx.ConnectError:
        logger.warning(f"⚠️ {socket} may not support HTTPS, falling back to HTTP protocol.")
        api_base_url = api_base_url.replace("https://", "http://")
        return False
    finally:
        logger.info(f"🎯 Using HTTP API base URL: {api_base_url}, game id: {game_id}")
    return True


asyncio.run(try_https())


async def get_game_info():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{api_base_url}/game/{game_id}", headers={"User-Agent": config.client_label})
        data = response.json()
        name = data.get("name")
        brief = data.get("brief")
        start_at = data.get("start_at")
        end_at = data.get("end_at")
        return f"""🎯 赛事: {name}\n简介: {brief}\n时间: {time.strftime("%Y/%m/%d %H:%M", time.localtime(start_at))} - {time.strftime("%Y/%m/%d %H:%M", time.localtime(end_at))}\n链接: {api_base_url.replace("/api", "")}/games/{game_id}"""


async def get_scoreboard(show_non_positive: bool = False):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{api_base_url}/game/{game_id}/team?page=1&page_size=10&order=score&asc=false&min_state=3", headers={"User-Agent": config.client_label})
        data = response.json()
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
                index += "."

            team_name = team.get("name")
            team_score = team.get("score")

            if team_score <= 0 and not show_non_positive:
                continue
            else:
                message += f"""\n{index} [{team_name}] {team_score} pts"""
        message += f"""\n更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        return message

