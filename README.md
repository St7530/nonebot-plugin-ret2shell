# nonebot-plugin-ret2shell

_✨ Ret 2 Shell (回归终端) 赛事事件播报与信息查询 ✨_


## 📖 介绍

对接 [Ret 2 Shell (回归终端)](https://ret.sh.cn/) **事件推送 WebSocket API**、**平台 HTTP API** 和 **生命周期 Webhook 服务**，实现赛事事件播报和信息查询功能。

## 💿 安装

在 NoneBot 机器人项目的根目录下执行插件安装命令：

    nb plugin install nonebot-plugin-ret2shell

## ⚙️ 配置

在 dotenv 配置文件中填入配置：

|        配置项         |  必填   |                    说明                     |
|:------------------:|:-----:|:-----------------------------------------:|
| RET2SHELL_WS_LINK  | **是** |          赛事事件推送 WebSocket API 链接          |
| RET2SHELL_ACCOUNT  |   否   |           赛事管理员用户名，留空则无法获取部分信息。           |
| RET2SHELL_PASSWORD |   否   |           赛事管理员密码，留空则无法获取部分信息。            |
|   WEBHOOK_ROUTE    |   否   |      Webhook 路由，推荐修改，默认为 `/webhook`       |
|  PUBLIC_GROUP_ID   |   否   |             比赛群号，留空则不会播报公开事件。             |
|   ADMIN_GROUP_ID   |   否   |             管理员号，留空则不会播报管理事件。             |
|       OPS_ID       |   否   |             管理员号，留空则不会播报运维事件。             |

示例：

```env
DRIVER=~fastapi+~websockets

RET2SHELL_WS_LINK=wss://ret.sh.cn/api/event/connect?game_id=1&token=mn7Me1rkMLUbJj-iyHbu0
RET2SHELL_ACCOUNT=_bot
RET2SHELL_PASSWORD=P@sSw0Rd
WEBHOOK_ROUTE=/WeBH00K
PUBLIC_GROUP_ID=123456789
ADMIN_GROUP_ID=987654321
OPS_ID=111222333
```

如需了解更多，请查看：[🔗 Wiki 文档](https://github.com/St7530/nonebot-plugin-ret2shell/wiki)


## 🎉 使用

安装、配置得当后，启动 NoneBot，[通过 OneBot V11 适配器连接 bot](https://onebot.adapters.nonebot.dev/docs/guide/setup/#onebot-v11)，插件即可开始工作。

### 查询指令表

|            指令             |          说明           |
|:-------------------------:|:---------------------:|
|           /game           |        查询赛事信息         |
|    /rank `[tag_name]`     | 查询单方向排行前十，参数留空则为总分前十。 |
| /challenge `challenge_id` |        查询题目信息         |
|      /team `team_id`      |        查询队伍信息         |