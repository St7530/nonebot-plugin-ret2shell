import time
import nonebot
from nonebot import logger
from .events import Event
from .config import config


def generate_event_msg(event: Event):
    message = ""
    timestamp = 0
    event_type = event.data.event_type.value
    is_debug_message = False

    if event.kind == "challenge":
        timestamp = event.data.challenge.updated_at
        challenge_tag_name = event.data.challenge.tag[0].name
        challenge_name = event.data.challenge.name

        if event_type == "new_hint":
            message = f"""💡[{challenge_tag_name}] 方向题目 [{challenge_name}] 提示更新，请前往比赛平台查看。"""
        elif event_type == "up":
            message = f"""⬆️[{challenge_tag_name}] 方向上新题目: [{challenge_name}]"""
        elif event_type == "down":
            message = f"""⬇️[{challenge_tag_name}] 方向下线题目: [{challenge_name}]"""

    elif event.kind == "submission":
        timestamp = event.data.submission.created_at
        blood_state = event.data.blood_state
        team_name = event.data.team.name
        challenge_tag_name = event.data.challenge.tag[0].name
        challenge_name = event.data.challenge.name

        if event_type == "correct":
            if blood_state == 1:
                message = f"""🥇恭喜队伍 [{team_name}] 获得 [{challenge_tag_name}] 方向题目 [{challenge_name}] 的 [一血] ！"""
            if blood_state == 2:
                message = f"""🥈恭喜队伍 [{team_name}] 获得 [{challenge_tag_name}] 方向题目 [{challenge_name}] 的 [二血] ！"""
            if blood_state == 3:
                message = f"""🥉恭喜队伍 [{team_name}] 获得 [{challenge_tag_name}] 方向题目 [{challenge_name}] 的 [三血] ！"""
        elif event_type == "cheated":
            message = f"""🤥队伍 [{team_name}] 在 [{challenge_tag_name}] 方向题目 [{challenge_name}] 中作弊！"""
            is_debug_message = True

    elif event.kind == "game":
        notification_title = event.data.message

        if event_type == "new_notification":
            message = f"""📰新通知: [{notification_title}]\n请前往比赛平台查看。"""

    elif event.kind == "chat":
        team_name = event.data.team.name
        challenge_tag_name = event.data.challenge.tag[0].name
        challenge_name = event.data.challenge.name
        content = event.data.content

        if event_type == "message":
            message = f"""✉️队伍 [{team_name}] 对 [{challenge_tag_name}] 方向题目 [{challenge_name}] 发送了锤子反馈: \n{content}"""
            is_debug_message = True

    elif event.kind == "devops":
        message = f"""👿DEVOPS EVENT"""
        is_debug_message = True

    if timestamp > 0:
        message += f"""\n时间: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))}"""
    return message, is_debug_message


async def send_event_msg(event: Event):
    message, is_debug_message = generate_event_msg(event)
    bot = nonebot.get_bot()

    if is_debug_message:
        logger.info(f"✉️ Sending private message: \n{message}")
        if config.admin_id:
            await bot.send_private_msg(user_id=config.admin_id, message=message)
    else:
        logger.info(f"✉️ Sending group message: \n{message}")
        if config.target_group_id:
            await bot.send_group_msg(group_id=config.target_group_id, message=message)

