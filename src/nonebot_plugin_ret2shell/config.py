from pydantic import BaseModel
from typing import Optional
from nonebot import get_plugin_config


class Config(BaseModel):
    ret2shell_ws_link: Optional[str] = None
    ret2shell_account: Optional[str] = None
    ret2shell_password: Optional[str] = None
    public_group_id: Optional[int] = None
    admin_group_id: Optional[int] = None
    ops_id: Optional[int] = None
    client_label: str = "nonebot-plugin-ret2shell"


config = get_plugin_config(Config)