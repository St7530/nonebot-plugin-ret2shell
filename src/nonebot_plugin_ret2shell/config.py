from pydantic import BaseModel
from typing import Optional
from nonebot import get_plugin_config


class Config(BaseModel):
    ret2shell_ws_link: Optional[str] = None
    target_group_id: Optional[int] = None
    admin_id: Optional[int] = None
    client_label: Optional[str] = "nonebot-plugin-ret2shell"


config = get_plugin_config(Config)