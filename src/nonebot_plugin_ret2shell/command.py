from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from .http_api import get_game_info, get_rank, get_tag_rank, get_challenge_info, get_team_info
from .config import config

game = on_command("game", aliases={"比赛", "赛事"})
rank = on_command("rank", aliases={"scoreboard", "排名", "积分板"})
challenge = on_command("challenge", aliases={"题目"})
team = on_command("team", aliases={"队伍"})


@game.handle()
async def handle_game():
    message = await get_game_info()
    await game.finish(message)


@rank.handle()
async def handle_rank(args: Message = CommandArg()):
    if tag := args.extract_plain_text():
        message = await get_tag_rank(tag.lower())
        if message is None:
            await challenge.finish("❔ 找不到该题目标签。", reply_message=True)
    else:
        message = await get_rank()
    await rank.finish(message)


@challenge.handle()
async def handle_challenge(args: Message = CommandArg()):
    if not config.ret2shell_account or not config.ret2shell_password:
        return
    elif challenge_id := args.extract_plain_text():
        message = await get_challenge_info(int(challenge_id))
        await challenge.finish(message, reply_message=True)
    else:
        await challenge.finish("❔ 请输入题目 id", reply_message=True)


@team.handle()
async def handle_team(args: Message = CommandArg()):
    if not config.ret2shell_account or not config.ret2shell_password:
        return
    elif team_id := args.extract_plain_text():
        message = await get_team_info(int(team_id))
        await team.finish(message, reply_message=True)
    else:
        await team.finish("❔ 请输入队伍 id", reply_message=True)

