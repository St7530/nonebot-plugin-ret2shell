# nonebot-plugin-ret2shell

_✨ 播报 Ret 2 Shell (回归终端) 比赛事件 ✨_


## 📖 介绍

接入 Ret 2 Shell (回归终端) 事件推送 API，根据比赛发生的事件类型，实时向指定的群组或管理员账号播报。

## 💿 安装

在 NoneBot 机器人项目的根目录下执行插件安装命令：

    nb plugin install nonebot-plugin-ret2shell

## ⚙️ 配置

在 dotenv 配置文件中填入配置：

| 配置项 | 必填 | 说明 |
|:-----:|:----:|:----:|
| RET2SHELL_WS_LINK | 是 | 平台事件推送 API 链接 |
| TARGET_GROUP_ID | 否 | 比赛群号 |
| ADMIN_ID | 否 | 管理员号 |

示例：
```env
DRIVER=~fastapi+~websockets

RET2SHELL_WS_LINK=ws://ret.sh.cn/api/event/connect?game_id=1&token=mn7Me1rkMLUbJj-iyHbu0
TARGET_GROUP_ID=123456789
ADMIN_ID=987654321
```
