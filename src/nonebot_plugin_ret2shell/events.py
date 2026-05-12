import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any, Union


# ---------- 枚举类（对应 Rust 中的枚举变体）----------
class ChallengeEventType(str, Enum):
    UP = "up"
    DOWN = "down"
    NEW_HINT = "new_hint"


class SubmissionEventType(str, Enum):
    CORRECT = "correct"
    CHEATED = "cheated"
    TOO_QUICK = "too_quick"


class GameEventType(str, Enum):
    FREEZE = "freeze"
    UNFREEZE = "unfreeze"
    NEW_NOTIFICATION = "new_notification"


class ChatEventType(str, Enum):
    MESSAGE = "message"


class DevopsEventType(str, Enum):
    CLUSTER_OVERLOADED = "cluster_overloaded"
    CLUSTER_RECOVERED = "cluster_recovered"
    SERVER_PANIC = "server_panic"


# ---------- 数据库模型类（对应 r2s_database 中的模型）----------
@dataclass
class Tag:
    name: str
    primary: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tag":
        return cls(name=data["name"], primary=data["primary"])


@dataclass
class ScoreRule:
    initial: int
    minimum: int
    decay: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScoreRule":
        return cls(initial=data["initial"], minimum=data["minimum"], decay=data["decay"])


@dataclass
class ChallengeModel:
    id: int
    name: str
    updated_at: int
    content: str
    hidden: bool
    game_id: int
    tag: List[Tag]
    score_rule: ScoreRule
    score: int
    bucket: str
    ref_id: Optional[int]
    release_at: Optional[int]
    archive_at: Optional[int]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChallengeModel":
        return cls(
            id=data["id"],
            name=data["name"],
            updated_at=data["updated_at"],
            content=data["content"],
            hidden=data["hidden"],
            game_id=data["game_id"],
            tag=[Tag.from_dict(t) for t in data["tag"]],
            score_rule=ScoreRule.from_dict(data["score_rule"]),
            score=data["score"],
            bucket=data["bucket"],
            ref_id=data.get("ref_id"),
            release_at=data.get("release_at"),
            archive_at=data.get("archive_at"),
        )


@dataclass
class UserModel:
    id: int
    registered_at: int
    account: str
    nickname: str
    email: Optional[str]
    description: Optional[str]
    avatar: Optional[str]
    institute_id: Optional[int]
    permissions: List[str]
    hidden: bool
    banned: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserModel":
        return cls(
            id=data["id"],
            registered_at=data["registered_at"],
            account=data["account"],
            nickname=data["nickname"],
            email=data.get("email"),
            description=data.get("description"),
            avatar=data.get("avatar"),
            institute_id=data.get("institute_id"),
            permissions=data.get("permissions", []),
            hidden=data.get("hidden", False),
            banned=data.get("banned", False),
        )


@dataclass
class TeamModel:
    id: int
    name: str
    game_id: int
    # 可根据实际需要添加更多字段，例如 affiliation, members 等

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TeamModel":
        # 简化版，假设 JSON 中至少包含 id, name, game_id
        return cls(
            id=data["id"],
            name=data["name"],
            game_id=data.get("game_id", 0),  # 默认值
        )


@dataclass
class SubmissionModel:
    id: int
    created_at: int
    user_id: int
    challenge_id: int
    team_id: int
    content: str
    solved: bool
    result: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SubmissionModel":
        return cls(
            id=data["id"],
            created_at=data["created_at"],
            user_id=data["user_id"],
            challenge_id=data["challenge_id"],
            team_id=data["team_id"],
            content=data["content"],
            solved=data["solved"],
            result=data["result"],
        )


# ---------- 事件结构体 ----------
@dataclass
class ChallengeEvent:
    challenge: ChallengeModel
    operator: UserModel
    event_type: ChallengeEventType

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChallengeEvent":
        return cls(
            challenge=ChallengeModel.from_dict(data["challenge"]),
            operator=UserModel.from_dict(data["operator"]),
            event_type=ChallengeEventType(data["event_type"]),
        )


@dataclass
class SubmissionEvent:
    submission: SubmissionModel
    blood_state: Optional[int]
    operator: UserModel
    team: Optional[TeamModel]
    challenge: ChallengeModel
    peer_team: Optional[TeamModel]
    reason: Optional[str]
    event_type: SubmissionEventType

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SubmissionEvent":
        return cls(
            submission=SubmissionModel.from_dict(data["submission"]),
            blood_state=data.get("blood_state"),
            operator=UserModel.from_dict(data["operator"]),
            team=TeamModel.from_dict(data["team"]) if data.get("team") else None,
            challenge=ChallengeModel.from_dict(data["challenge"]),
            peer_team=TeamModel.from_dict(data["peer_team"]) if data.get("peer_team") else None,
            reason=data.get("reason"),
            event_type=SubmissionEventType(data["event_type"]),
        )


@dataclass
class GameEvent:
    operator: UserModel
    event_type: GameEventType
    message: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameEvent":
        return cls(
            operator=UserModel.from_dict(data["operator"]),
            event_type=GameEventType(data["event_type"]),
            message=data["message"],
        )


@dataclass
class ChatEvent:
    operator: UserModel
    team: TeamModel
    challenge: ChallengeModel
    event_type: ChatEventType
    content: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatEvent":
        return cls(
            operator=UserModel.from_dict(data["operator"]),
            team=TeamModel.from_dict(data["team"]),
            challenge=ChallengeModel.from_dict(data["challenge"]),
            event_type=ChatEventType(data["event_type"]),
            content=data["content"],
        )


@dataclass
class DevopsEvent:
    event_type: DevopsEventType
    running: Optional[int]
    pending: Optional[int]
    message: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DevopsEvent":
        return cls(
            event_type=DevopsEventType(data["event_type"]),
            running=data.get("running"),
            pending=data.get("pending"),
            message=data.get("message"),
        )


# ---------- 顶层事件枚举（模拟 Rust 的 Event 枚举）----------
class Event:
    """等效于 Rust 中的 Event 枚举，根据 JSON 中唯一的键确定具体类型"""
    def __init__(self, kind: str, data: Any):
        self.kind = kind          # "challenge", "submission", "game", "chat", "devops"
        self.data = data          # 对应的具体事件对象

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        # data 应只包含一个键，例如 {"challenge": {...}} 或 {"submission": {...}}
        if len(data) != 1:
            raise ValueError(f"Event object must have exactly one key, got {len(data)}")
        kind, value = next(iter(data.items()))
        if kind == "challenge":
            event_obj = ChallengeEvent.from_dict(value)
        elif kind == "submission":
            event_obj = SubmissionEvent.from_dict(value)
        elif kind == "game":
            event_obj = GameEvent.from_dict(value)
        elif kind == "chat":
            event_obj = ChatEvent.from_dict(value)
        elif kind == "devops":
            event_obj = DevopsEvent.from_dict(value)
        else:
            raise ValueError(f"Unknown event kind: {kind}")
        return cls(kind, event_obj)

    def to_dict(self) -> Dict[str, Any]:
        """将 Event 对象转换回字典，便于序列化为 JSON"""
        if self.kind == "challenge":
            return {self.kind: _asdict(self.data)}
        elif self.kind == "submission":
            return {self.kind: _asdict(self.data)}
        elif self.kind == "game":
            return {self.kind: _asdict(self.data)}
        elif self.kind == "chat":
            return {self.kind: _asdict(self.data)}
        elif self.kind == "devops":
            return {self.kind: _asdict(self.data)}
        else:
            raise ValueError(f"Unknown event kind: {self.kind}")


# 辅助函数：将 dataclass 对象递归转换为字典
def _asdict(obj):
    """比 dataclasses.asdict 更简单地处理枚举和嵌套对象"""
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, list):
        return [_asdict(i) for i in obj]
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for field_name, field_def in obj.__dataclass_fields__.items():
            value = getattr(obj, field_name)
            result[field_name] = _asdict(value)
        return result
    return obj


@dataclass
class EventContainer:
    game_id: int
    event: Event

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventContainer":
        return cls(
            game_id=data["game_id"],
            event=Event.from_dict(data["event"]),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "game_id": self.game_id,
            "event": self.event.to_dict(),
        }


# ---------- 广播枚举 ----------
class Broadcast:
    """等效于 Rust 中的 Broadcast 枚举"""
    def __init__(self, kind: str, data: Optional[EventContainer] = None):
        self.kind = kind  # "publish" 或 "heartbeat"
        self.data = data  # 当 kind 为 "publish" 时包含 EventContainer

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Broadcast":
        # data 应包含一个键："Publish" 或 "Heartbeat"
        if "Publish" in data:
            return cls("publish", EventContainer.from_dict(data["Publish"]))
        elif "Heartbeat" in data:
            return cls("heartbeat", None)
        else:
            raise ValueError("Broadcast object must have key 'Publish' or 'Heartbeat'")

    def to_dict(self) -> Dict[str, Any]:
        if self.kind == "publish":
            return {"Publish": self.data.to_dict()}
        else:
            return {"Heartbeat": None}


# ---------- 从 JSON 字符串反序列化的统一入口 ----------
def from_json(json_str: str, target_class):
    """
    从 JSON 字符串反序列化为指定类的实例。
    target_class 可以是 EventContainer, Broadcast 或任何实现了 from_dict 的类。
    """
    data = json.loads(json_str)
    return target_class.from_dict(data)

