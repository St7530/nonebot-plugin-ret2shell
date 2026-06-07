from nonebot.plugin import PluginMetadata

from .config import config, Config

__plugin_meta__ = PluginMetadata(
    # 基本信息（必填）
    name="Ret 2 Shell 播报与查询",  # 插件名称
    description="Ret 2 Shell (回归终端) 赛事事件播报与信息查询",  # 插件介绍
    usage="详见 README",  # 插件用法

    # 发布额外信息
    type="application",  # 插件分类
    # 发布必填，当前有效类型有：`library`（为其他插件编写提供功能），`application`（向机器人用户提供功能）。

    homepage="https://github.com/St7530/nonebot-plugin-ret2shell",
    # 发布必填。

    config=Config,
    # 插件配置项类，如果有配置类则必须填写。

    supported_adapters={"~onebot.v11"},
    # 支持的适配器集合，其中 `~` 在此处代表前缀 `nonebot.adapters.`，其余适配器亦按此格式填写。
    # 若插件只使用了 NoneBot 基本抽象，应显式填写 None，否则应该列出插件支持的适配器。
)

from nonebot import logger

if not config.ret2shell_account or not config.ret2shell_password:
    logger.opt(colors=True).warning('😪 "<y>RET2SHELL_ACCOUNT</y>" or "<y>RET2SHELL_PASSWORD</y>" not set, some details won\'t be fetched.')
    logger.opt(colors=True).warning('😪 "<y>RET2SHELL_ACCOUNT</y>" or "<y>RET2SHELL_PASSWORD</y>" not set, some inquiries won\'t be handled.')
if not config.public_group_id:
    logger.opt(colors=True).warning('😪 "<y>TARGET_GROUP_ID</y>" not set, group messages won\'t be sent.')
if not config.ops_id:
    logger.opt(colors=True).warning('😪 "<y>ADMIN_ID</y>" not set, private messages won\'t be sent.')

if not config.ret2shell_ws_link:
    logger.opt(colors=True).critical('😪 "<y>RET2SHELL_WS_LINK</y>" not set, the plugin won\'t function.')
else:
    from . import command, ws_client, webhook

