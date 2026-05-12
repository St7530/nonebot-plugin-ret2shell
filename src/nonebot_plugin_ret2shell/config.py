from pydantic import BaseModel
from typing import Optional


class Config(BaseModel):
    ret2shell_ws_link: Optional[str] = None
    target_group_id: Optional[int] = None
    admin_id: Optional[int] = None

