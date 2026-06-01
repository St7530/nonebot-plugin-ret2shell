# nonebot-plugin-ret2shell

_✨ Ret 2 Shell (回归终端) 比赛事件播报与信息查询 ✨_


## 📖 介绍

接入 Ret 2 Shell (回归终端) 事件推送 API，根据比赛发生的事件类型，实时向指定的群组或管理员账号播报，同时具有主动查询功能。

[🔗 Wiki 文档](https://github.com/St7530/nonebot-plugin-ret2shell/wiki)

## 💿 安装

在 NoneBot 机器人项目的根目录下执行插件安装命令：

    nb plugin install nonebot-plugin-ret2shell

## ⚙️ 配置

在 dotenv 配置文件中填入配置：

|         配置项        | 必填 |                  说明                  |
|:------------------:|:----:|:------------------------------------:|
| RET2SHELL_WS_LINK  | 是 |       赛事事件推送 WebSocket API 链接        |
| RET2SHELL_ACCOUNT  | 否 |        赛事管理员用户名，留空则无法获取部分信息。         |
| RET2SHELL_PASSWORD | 否 |        赛事管理员密码，留空则无法获取部分信息。        |
|  TARGET_GROUP_ID   | 否 |          比赛群号，留空则不会播报公开事件。           |
|      ADMIN_ID      | 否 |          管理员号，留空则不会播报管理事件。           |
|    CLIENT_LABEL    | 否 | 客户端标识，默认为 `nonebot-plugin-ret2shell` |

示例：
```env
DRIVER=~fastapi+~websockets

RET2SHELL_WS_LINK=wss://ret.sh.cn/api/event/connect?game_id=1&token=mn7Me1rkMLUbJj-iyHbu0
RET2SHELL_ACCOUNT=_bot
RET2SHELL_PASSWORD=P@sSw0Rd
TARGET_GROUP_ID=123456789
ADMIN_ID=987654321
```


## 🎉 使用

通过 OneBot V11 适配器连接 bot 后，插件会尝试与 Ret 2 Shell 赛事事件推送 API 建立连接，然后播报事件。

当 bot 连接断开后，插件也会与平台断开连接，以节省资源。

### 查询指令表

|           指令            |   说明   |
|:-----------------------:|:------:|
|          /game          | 查询赛事信息 |
|          /rank          | 查询积分板  |
| /challenge `challenge_id` | 查询题目信息 |
|      /team `team_id`      | 查询队伍信息 |