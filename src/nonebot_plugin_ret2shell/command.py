from .http_api import get_game_info, get_scoreboard

from nonebot import on_command, logger

game = on_command("game", aliases={"比赛"})
rank = on_command("rank", aliases={"排名"})
plugin_help = on_command("help", aliases={"帮助"})


@game.handle()
async def handle_game():
    message = await get_game_info()
    await game.finish(message)


@rank.handle()
async def handle_rank():
    message = await get_scoreboard()
    await rank.finish(message)


@plugin_help.handle()
async def handle_help():
    message = """🧩 nonebot-plugin-ret2shell\n/game 查看比赛信息\n/rank 查看比赛积分板"""
    await plugin_help.finish(message)

