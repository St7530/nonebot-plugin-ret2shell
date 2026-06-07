import json
import time
from datetime import datetime
import nonebot
from nonebot import logger, get_driver
from nonebot import require
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
from .events import Event
from .http_api import init_http_api, get_game_timestamp, get_hint_details, get_notification_details
from .config import config


async def send_public_msg(message: str):
    logger.info(f"✉️ Generated public message: \n{message}")
    if config.public_group_id:
        for bot in nonebot.get_bots().values():
            await bot.send_group_msg(group_id=config.public_group_id, message=message)


async def send_admin_msg(message: str):
    logger.info(f"✉️ Generated admin message: \n{message}")
    if config.admin_group_id:
        for bot in nonebot.get_bots().values():
            await bot.send_group_msg(group_id=config.admin_group_id, message=message)


async def send_ops_msg(message: str):
    logger.info(f"✉️ Generated ops message: \n{message}")
    if config.ops_id:
        for bot in nonebot.get_bots().values():
            await bot.send_private_msg(user_id=config.ops_id, message=message)


async def generate_event_msg(event: Event):
    event_type = event.data.event_type.value
    message: str = "❔ 未知事件"
    timestamp: int = 0
    msg_type: str = "ops"

    if event.kind == "challenge":
        timestamp = event.data.challenge.updated_at
        challenge_tag_name = event.data.challenge.tag[0].name
        challenge_name = event.data.challenge.name
        msg_type = "public"

        if event_type == "up":
            message = f"""⬆️ [{challenge_tag_name}] 方向上新题目: [{challenge_name}]"""
        elif event_type == "down":
            message = f"""⬇️ [{challenge_tag_name}] 方向下线题目: [{challenge_name}]"""
        elif event_type == "new_hint":
            challenge_id = event.data.challenge.id
            if config.ret2shell_account and config.ret2shell_password:
                hint_cost, hint_content, timestamp = await get_hint_details(challenge_id)
                if hint_cost == 0:
                    message = f"""💡 [{challenge_tag_name}] 方向题目 [{challenge_name}] 提示更新，无需花费分数: \n\n{hint_content}\n"""
                else:
                    message = f"""💡 [{challenge_tag_name}] 方向题目 [{challenge_name}] 提示更新，需花费 {hint_cost} pts 解锁，请前往比赛平台查看。"""
            else:
                message = f"""💡 [{challenge_tag_name}] 方向题目 [{challenge_name}] 提示更新，请前往比赛平台查看。"""

    elif event.kind == "submission":
        timestamp = event.data.submission.created_at
        challenge_tag_name = event.data.challenge.tag[0].name
        challenge_name = event.data.challenge.name

        if event_type == "correct":
            blood_state = event.data.blood_state
            team_name = event.data.team.name
            msg_type = "public"
            if blood_state == 1:
                message = f"""🥇 恭喜队伍 [{team_name}] 获得 [{challenge_tag_name}] 方向题目 [{challenge_name}] 的 [一血] ！"""
            if blood_state == 2:
                message = f"""🥈 恭喜队伍 [{team_name}] 获得 [{challenge_tag_name}] 方向题目 [{challenge_name}] 的 [二血] ！"""
            if blood_state == 3:
                message = f"""🥉 恭喜队伍 [{team_name}] 获得 [{challenge_tag_name}] 方向题目 [{challenge_name}] 的 [三血] ！"""
        elif event_type == "cheated":
            team_name = event.data.team.name
            peerteam_name = event.data.peer_team.name
            message = f"""🤥 [{challenge_tag_name}] 方向题目 [{challenge_name}] 发生作弊！\n队伍 [{team_name}] 提交了队伍 [{peerteam_name}] 的 flag"""
            msg_type = "admin"
        elif event_type == "too_quick":
            operator_name = event.data.operator.nickname
            message = f"""💥️ 选手 [{operator_name}] 在 [{challenge_tag_name}] 方向题目 [{challenge_name}] 中提交频率过快！"""
            msg_type = "admin"

    elif event.kind == "game":
        msg_type = "public"

        if event_type == "new_notification":
            notification_title = event.data.message
            if config.ret2shell_account and config.ret2shell_password:
                notification_content, timestamp = await get_notification_details(notification_title)
                message = f"""📢 新通知: [{notification_title}]\n\n{notification_content}\n"""
            else:
                message = f"""📢 新通知: [{notification_title}]\n请前往比赛平台查看。"""

        if event_type == "freeze":
            message = """🧊 比赛已冻结。"""
        if event_type == "unfreeze":
            message = """🌊 比赛已解冻。"""

    elif event.kind == "chat":
        team_name = event.data.team.name
        challenge_tag_name = event.data.challenge.tag[0].name
        challenge_name = event.data.challenge.name
        content = event.data.content
        msg_type = "public"

        if event_type == "message":
            message = f"""✉️ 队伍 [{team_name}] 对 [{challenge_tag_name}] 方向题目 [{challenge_name}] 发送了锤子反馈: \n\n{content}"""

    elif event.kind == "devops":
        msg_type = "ops"

        if event_type == "cluster_overloaded":
            message = """👿 集群超载\n"""
        if event_type == "cluster_recovered":
            message = """👿 集群恢复\n"""
        if event_type == "server_panic":
            message = """👿 服务崩溃\n"""

        message += json.dumps(event.to_dict())

    if timestamp > 0:
        message += f"""\n时间: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))}"""
    return message, msg_type


async def send_event_msg(event: Event):
    message, msg_type = await generate_event_msg(event)
    if msg_type == "public":
        await send_public_msg(message)
    elif msg_type == "admin":
        await send_admin_msg(message)
    elif msg_type == "ops":
        await send_ops_msg(message)


async def task_game_start():
    message = """🏁 比赛已开始！"""
    await send_public_msg(message)


async def task_game_end():
    message = """🎉 比赛已结束。"""
    await send_public_msg(message)


driver = get_driver()
@driver.on_startup
async def schedule_tasks():
    await init_http_api()
    start_timestamp, end_timestamp = await get_game_timestamp()
    start_time = datetime.fromtimestamp(start_timestamp)
    end_time = datetime.fromtimestamp(end_timestamp)
    logger.opt(colors=True).info(f'🎯 Game starts at "<y>{start_time}</y>", ends at "<y>{end_time}</y>". Scheduling tasks...')
    scheduler.add_job(
        task_game_start, "date", run_date=start_time
    )
    scheduler.add_job(
        task_game_end, "date", run_date=end_time
    )

