from __future__ import annotations

from app.team.analytics import fit_performance, recompute_fit_rows


def test_fit_performance_orders_results_without_saturating_common_ranks():
    top = fit_performance(1, 2000, score=500, max_score=500, solved=5)
    middle = fit_performance(500, 2000, score=300, max_score=500, solved=3)
    lower = fit_performance(1500, 2000, score=100, max_score=500, solved=1)
    assert top > middle > lower
    assert top < 2800


def test_recompute_fit_rows_is_monotonic_over_time():
    rows = [
        {"id": 1, "contest_time": "2026-01-01", "rank": 80, "participants": 1000},
        {"id": 2, "contest_time": "2026-01-08", "rank": 10, "participants": 1000},
    ]
    result = recompute_fit_rows(rows)
    assert result[0]["fitted_rating"] < result[1]["fitted_rating"]

