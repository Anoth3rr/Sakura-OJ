from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


Language = Literal["c", "cpp", "cpp17", "python", "pypy", "java"]
Role = Literal["admin", "problem_admin", "teacher", "student"]


class TestCaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    input_data: str = Field(max_length=100_000)
    expected_output: str = Field(max_length=100_000)
    is_sample: bool = False
    weight: int = Field(default=1, ge=1, le=100)


class ProblemCreate(BaseModel):
    slug: str = Field(min_length=2, max_length=80, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=20_000)
    statement_markdown: str | None = Field(default=None, max_length=50_000)
    input_format: str = Field(min_length=1, max_length=5_000)
    output_format: str = Field(min_length=1, max_length=5_000)
    difficulty: str = Field(default="入门", min_length=1, max_length=20)
    time_limit_ms: int = Field(default=1_000, ge=100, le=30_000)
    memory_limit_mb: int = Field(default=256, ge=16, le=2_048)
    test_cases: list[TestCaseCreate] = Field(default_factory=list, max_length=500)

    @field_validator("title", "input_format", "output_format", "difficulty")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("文本不能为空")
        return value

    @model_validator(mode="after")
    def require_statement(self) -> "ProblemCreate":
        markdown = (self.statement_markdown or "").strip()
        description = (self.description or "").strip()
        if not markdown and not description:
            raise ValueError("statement_markdown 或 description 至少提供一个")
        if not markdown:
            self.statement_markdown = description
        if not description:
            self.description = markdown
        return self


class TestCaseSample(BaseModel):
    id: int
    name: str
    input_data: str
    expected_output: str


class ProblemSummary(BaseModel):
    id: int
    problem_code: str
    slug: str
    title: str
    difficulty: str
    time_limit_ms: int
    memory_limit_mb: int
    submission_count: int = 0
    accepted_count: int = 0
    created_at: str
    judge_mode: str = 'normal'


class ProblemDetail(ProblemSummary):
    description: str
    statement_markdown: str
    statement_html: str
    input_format: str
    input_format_html: str
    output_format: str
    output_format_html: str
    test_cases: list[TestCaseSample]


class ProblemListResponse(BaseModel):
    items: list[ProblemSummary]
    total: int
    page: int
    page_size: int


class ProblemBankAdd(BaseModel):
    problem_code: str = Field(min_length=1, max_length=20)


class LanguageInfo(BaseModel):
    id: str
    label: str
    available: bool


class SubmissionCreate(BaseModel):
    problem_id: int | None = Field(default=None, ge=1)
    problem_slug: str | None = Field(default=None, min_length=2, max_length=80)
    language: Language = "cpp"
    # Keep request validation above the configurable byte limit so the route can
    # return a precise 413 response for oversized source files.
    source_code: str = Field(min_length=1, max_length=2_000_000)

    @model_validator(mode="after")
    def require_problem(self) -> "SubmissionCreate":
        if self.problem_id is None and self.problem_slug is None:
            raise ValueError("problem_id 或 problem_slug 至少提供一个")
        return self


class SubmissionAccepted(BaseModel):
    id: str
    problem_id: int
    problem_slug: str
    language: str
    status: str
    verdict: str
    score: int
    created_at: str


class SubmissionResult(BaseModel):
    test_case_id: int
    test_case_name: str
    verdict: str
    score: int
    runtime_ms: int | None
    output: str
    error_message: str
    memory_kb: int | None = None
    message_bytes: int | None = None


class SubmissionDetail(BaseModel):
    id: str
    problem_id: int
    problem_slug: str
    problem_title: str
    language: str
    source_code: str
    status: str
    verdict: str
    score: int
    compile_output: str
    error_message: str
    runtime_ms: int | None
    memory_kb: int | None
    created_at: str
    started_at: str | None
    finished_at: str | None
    results: list[SubmissionResult]


class SubmissionListResponse(BaseModel):
    items: list[SubmissionAccepted]
    total: int


class StatsResponse(BaseModel):
    problem_count: int
    submission_count: int
    accepted_count: int
    acceptance_rate: float


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    role: Role
    role_label: str
    is_active: bool = True


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_][A-Za-z0-9_.-]*$")
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=80)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("用户名不能为空")
        return value


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=32)
    password: str = Field(min_length=1, max_length=128)


class UserCreateRequest(RegisterRequest):
    role: Role = "student"

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value: str) -> str:
        aliases = {
            "administrator": "admin",
            "管理员": "admin",
            "question_admin": "problem_admin",
            "题目管理员": "problem_admin",
            "老师": "teacher",
            "学生": "student",
        }
        return aliases.get(str(value).strip(), str(value).strip())


class UserUpdateRequest(BaseModel):
    role: Role | None = None
    display_name: str | None = Field(default=None, min_length=1, max_length=80)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_active: bool | None = None

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value: str | None) -> str | None:
        if value is None:
            return None
        aliases = {
            "administrator": "admin",
            "管理员": "admin",
            "question_admin": "problem_admin",
            "题目管理员": "problem_admin",
            "老师": "teacher",
            "学生": "student",
        }
        return aliases.get(str(value).strip(), str(value).strip())


class AuthResponse(BaseModel):
    user: UserResponse
