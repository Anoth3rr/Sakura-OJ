from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


Platform = Literal["codeforces", "atcoder", "nowcoder"]


class MemberCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    student_id: str = Field(default="", max_length=40)
    team_group: str = Field(default="算法组", max_length=40)
    status: Literal["active", "paused", "graduated"] = "active"
    color: str = Field(default="#2dd4bf", max_length=20, pattern=r"^#[0-9A-Fa-f]{6}$")
    cf_handle: str = Field(default="", max_length=80)
    atcoder_handle: str = Field(default="", max_length=80)
    nowcoder_handle: str = Field(default="", max_length=80)
    nowcoder_uid: str = Field(default="", pattern=r"^(?:[1-9][0-9]{0,18})?$")
    oj_username: str = Field(default="", max_length=80)
    email: str = Field(default="", max_length=120)
    note: str = Field(default="", max_length=2000)

    @field_validator("name", "student_id", "team_group", "cf_handle", "atcoder_handle", "nowcoder_handle", "oj_username", "email", "note")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("nowcoder_uid", mode="before")
    @classmethod
    def normalize_uid(cls, value: Any) -> Any:
        return str(value).strip() if isinstance(value, (str, int)) and not isinstance(value, bool) else value

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value: str) -> str:
        return {"训练中": "active", "暂休": "paused", "毕业": "graduated"}.get(str(value).strip(), str(value).strip())


class MemberUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    student_id: str | None = Field(default=None, max_length=40)
    team_group: str | None = Field(default=None, max_length=40)
    status: Literal["active", "paused", "graduated"] | None = None
    color: str | None = Field(default=None, max_length=20, pattern=r"^#[0-9A-Fa-f]{6}$")
    cf_handle: str | None = Field(default=None, max_length=80)
    atcoder_handle: str | None = Field(default=None, max_length=80)
    nowcoder_handle: str | None = Field(default=None, max_length=80)
    nowcoder_uid: str | None = Field(default=None, pattern=r"^(?:[1-9][0-9]{0,18})?$")
    oj_username: str | None = Field(default=None, max_length=80)
    email: str | None = Field(default=None, max_length=120)
    note: str | None = Field(default=None, max_length=2000)

    @field_validator("name", "student_id", "team_group", "cf_handle", "atcoder_handle", "nowcoder_handle", "oj_username", "email", "note")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @field_validator("nowcoder_uid", mode="before")
    @classmethod
    def normalize_uid(cls, value: Any) -> Any:
        return MemberCreate.normalize_uid(value)

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return {"训练中": "active", "暂休": "paused", "毕业": "graduated"}.get(str(value).strip(), str(value).strip())


class SyncRequest(BaseModel):
    platforms: list[Platform] = Field(default_factory=lambda: ["codeforces", "atcoder", "nowcoder"])


class ContestResultInput(BaseModel):
    member_id: int = Field(ge=1)
    rank: int = Field(ge=1)
    participants: int = Field(default=0, ge=0)
    score: float | None = None
    max_score: float | None = None
    solved: int | None = Field(default=None, ge=0)
    penalty: int | None = Field(default=None, ge=0)
    old_rating: int | None = None
    new_rating: int | None = None


class ContestImport(BaseModel):
    platform: str = Field(min_length=2, max_length=30)
    external_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=160)
    contest_time: str
    participant_count: int = Field(default=0, ge=0)
    results: list[ContestResultInput] = Field(min_length=1, max_length=500)


class OJSyncRequest(BaseModel):
    member_id: int | None = Field(default=None, ge=1)


class RatingImport(BaseModel):
    member_id: int = Field(ge=1)
    platform: Platform
    rating: int = Field(ge=0, le=5000)
    peak_rating: int | None = Field(default=None, ge=0, le=5000)
    rank_title: str = Field(default="", max_length=80)
    contest_count: int = Field(default=0, ge=0)
    rating_change: int = Field(default=0, ge=-5000, le=5000)


class SubmissionImport(BaseModel):
    platform: str = Field(min_length=2, max_length=30)
    member_id: int | None = Field(default=None, ge=1)
    items: list[dict[str, Any]] = Field(min_length=1, max_length=5000)
