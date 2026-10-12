from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from math import log2
from typing import Any


PLATFORMS = ("codeforces", "atcoder", "nowcoder")
PLATFORM_LABELS = {
    "codeforces": "Codeforces",
    "atcoder": "AtCoder",
    "nowcoder": "NowCoder",
    "oj": "Sakura OJ",
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def fit_performance(
    rank: int | None,
    participants: int | None,
    *,
    score: float | None = None,
    max_score: float | None = None,
    solved: int | None = None,
) -> int:
    """Map an online contest result to a stable cross-platform performance score.

    The percentile term handles rank, while a small field-size correction avoids
    treating a top-10 result in a 40-person practice contest like a top-10 result
    in a 40,000-person rated round. Score/solved are optional because providers
    expose different result shapes.
    """

    safe_rank = max(1, int(rank or 1))
    field = max(safe_rank, int(participants or safe_rank * 2), 20)
    percentile = clamp(1 - (safe_rank - 1) / max(1, field - 1), 0.01, 0.999)
    # A compressed curve keeps common top-50 results below the ceiling while
    # still rewarding a strong percentile in a large field.
    rating = 650 + 1450 * (percentile**2.4)
    rating += 24 * log2(max(1.0, field / safe_rank))
    if score is not None and max_score and max_score > 0:
        rating += 75 * clamp(float(score) / float(max_score), 0.0, 1.0)
    if solved is not None:
        rating += min(60, max(0, int(solved)) * 10)
    return int(round(clamp(rating, 600, 2800)))


def recompute_fit_rows(rows: list[dict[str, Any]], initial: int = 1200) -> list[dict[str, Any]]:
    """Return rows with performance_rating and exponentially smoothed fitted_rating."""

    previous = initial
    output: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: (item.get("contest_time") or "", item.get("id", 0))):
        performance = fit_performance(
            row.get("rank"),
            row.get("participants"),
            score=row.get("score"),
            max_score=row.get("max_score"),
            solved=row.get("solved"),
        )
        official = row.get("new_rating")
        target = performance if official is None else 0.68 * float(official) + 0.32 * performance
        fitted = int(round(0.66 * previous + 0.34 * target))
        row = dict(row)
        row["performance_rating"] = performance
        row["fitted_rating"] = fitted
        previous = fitted
        output.append(row)
    return output


def rating_tier(rating: int | float | None) -> str:
    score = int(rating or 0)
    if score >= 2400:
        return "顶尖" 
    if score >= 2100:
        return "竞赛级"
    if score >= 1800:
        return "进阶"
    if score >= 1500:
        return "稳步上升"
    return "基础期"


def build_profile(
    *,
    member: dict[str, Any],
    ratings: list[dict[str, Any]],
    contest_results: list[dict[str, Any]],
    submissions: list[dict[str, Any]],
) -> dict[str, Any]:
    accepted = sum(1 for item in submissions if item.get("verdict") in {"ACCEPTED", "AC"})
    total = len(submissions)
    acceptance_rate = round(accepted / total * 100, 1) if total else 0.0
    solved = sum(int(item.get("solved") or 0) for item in contest_results)
    contest_count = len(contest_results)
    performances = [int(item.get("performance_rating") or 0) for item in contest_results]
    current = max((int(item.get("rating") or 0) for item in ratings), default=0)
    fitted = int(contest_results[-1].get("fitted_rating") or current or 1200) if contest_results else current
    peak = max(
        [int(item.get("peak_rating") or 0) for item in ratings]
        + [int(item.get("fitted_rating") or 0) for item in contest_results]
        + [0]
    )
    recent = contest_results[-5:]
    recent_avg = round(sum(int(item.get("performance_rating") or 0) for item in recent) / len(recent)) if recent else fitted
    consistency = 0
    if len(performances) >= 2:
        mean = sum(performances) / len(performances)
        variance = sum((value - mean) ** 2 for value in performances) / len(performances)
        consistency = int(round(clamp(100 - variance**0.5 / 5, 0, 100)))
    elif performances:
        consistency = 72

    language_counter = Counter(str(item.get("language") or "unknown") for item in submissions)
    top_language = language_counter.most_common(1)[0][0] if language_counter else "-"
    tags: list[str] = []
    if acceptance_rate >= 80:
        tags.append("稳定 AC")
    elif acceptance_rate >= 55:
        tags.append("解题节奏")
    if recent_avg >= fitted + 80:
        tags.append("上升通道")
    elif recent_avg < fitted - 100:
        tags.append("需要复盘")
    if consistency >= 75:
        tags.append("发挥稳定")
    if solved >= 20:
        tags.append("赛场执行")
    if top_language not in {"-", "unknown"}:
        tags.append(f"主力 {top_language}")
    if not tags:
        tags.append("持续训练")

    return {
        "member_id": member["id"],
        "headline": rating_tier(fitted),
        "current_rating": fitted or current or 1200,
        "peak_rating": peak or fitted or current or 1200,
        "acceptance_rate": acceptance_rate,
        "contest_count": contest_count,
        "solved_count": solved,
        "consistency": consistency,
        "top_language": top_language,
        "tags": tags,
        "summary": _profile_summary(member, fitted or current or 1200, acceptance_rate, contest_count, recent_avg),
    }


def _profile_summary(member: dict[str, Any], rating: int, acceptance: float, contests: int, recent_avg: int) -> str:
    name = member.get("name") or member.get("display_name") or "队员"
    if contests == 0:
        return f"{name} 尚未导入比赛记录，先完成一次线上比赛同步。"
    direction = "保持上升" if recent_avg >= rating else "进入复盘周期"
    return f"{name} 当前拟合 rating {rating}，近况表现 {recent_avg}，AC 率 {acceptance:.1f}%，建议继续{direction}。"


def utc_iso(value: datetime | None = None) -> str:
    return (value or datetime.now(timezone.utc)).isoformat()
