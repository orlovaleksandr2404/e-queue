import pytest

from src.schemas.algorithm import Candidate
from src.services import algorithm


def test_select_next_empty_list(dt):
    result = algorithm.select_next([], None)
    assert result.ticket_id is None
    assert result.reason == "none_available"


def test_select_next_all_filtered_out(dt):
    candidates = [
        Candidate(id=1, priority=0, created_at=dt(0), service_id=10),
        Candidate(id=2, priority=0, created_at=dt(5), service_id=20),
    ]
    result = algorithm.select_next(candidates, window_service_ids=[99])
    assert result.ticket_id is None
    assert result.reason == "none_available"


def test_select_next_empty_window_services_means_no_filter(dt):
    candidates = [
        Candidate(id=1, priority=0, created_at=dt(0), service_id=10),
        Candidate(id=2, priority=0, created_at=dt(5), service_id=20),
    ]
    result = algorithm.select_next(candidates, window_service_ids=[])
    assert result.ticket_id == 1
    assert result.reason == "fifo"


def test_select_next_priority_wins_over_earlier_time(dt):
    candidates = [
        Candidate(id=1, priority=0,  created_at=dt(0),  service_id=1),
        Candidate(id=2, priority=20, created_at=dt(60), service_id=1),
    ]
    result = algorithm.select_next(candidates, [1])
    assert result.ticket_id == 2
    assert result.reason == "priority"


def test_select_next_fifo_inside_same_priority(dt):
    candidates = [
        Candidate(id=3, priority=0, created_at=dt(30), service_id=1),
        Candidate(id=1, priority=0, created_at=dt(10), service_id=1),
        Candidate(id=2, priority=0, created_at=dt(20), service_id=1),
    ]
    result = algorithm.select_next(candidates, [1])
    assert result.ticket_id == 1
    assert result.reason == "fifo"


def test_select_next_priority_order_desc(dt):
    candidates = [
        Candidate(id=1, priority=10, created_at=dt(0), service_id=1),
        Candidate(id=2, priority=30, created_at=dt(0), service_id=1),
        Candidate(id=3, priority=20, created_at=dt(0), service_id=1),
    ]
    result = algorithm.select_next(candidates, [1])
    assert result.ticket_id == 2


def test_select_next_priority_then_time(dt):
    candidates = [
        Candidate(id=1, priority=20, created_at=dt(50), service_id=1),
        Candidate(id=2, priority=20, created_at=dt(10), service_id=1),
        Candidate(id=3, priority=0,  created_at=dt(0),  service_id=1),
    ]
    result = algorithm.select_next(candidates, [1])
    assert result.ticket_id == 2


def test_select_next_deterministic_tie_break_by_id(dt):
    t = dt(0)
    candidates = [
        Candidate(id=5, priority=0, created_at=t, service_id=1),
        Candidate(id=2, priority=0, created_at=t, service_id=1),
        Candidate(id=9, priority=0, created_at=t, service_id=1),
    ]
    r1 = algorithm.select_next(candidates, [1])
    r2 = algorithm.select_next(list(reversed(candidates)), [1])
    assert r1.ticket_id == r2.ticket_id == 2


def test_position_target_alone(dt):
    t = Candidate(id=1, priority=0, created_at=dt(0), service_id=1)
    assert algorithm.compute_position(t, [t]) == 1


def test_position_target_not_in_queue(dt):
    target = Candidate(id=99, priority=0, created_at=dt(50), service_id=1)
    queue = [
        Candidate(id=1, priority=0, created_at=dt(0), service_id=1),
        Candidate(id=2, priority=0, created_at=dt(10), service_id=1),
    ]
    assert algorithm.compute_position(target, queue) == 3


def test_position_empty_queue(dt):
    target = Candidate(id=1, priority=0, created_at=dt(0), service_id=1)
    assert algorithm.compute_position(target, []) == 1


def test_position_priority_pushes_ahead(dt):
    target = Candidate(id=2, priority=20, created_at=dt(60), service_id=1)
    queue = [
        Candidate(id=1, priority=0, created_at=dt(0),  service_id=1),
        Candidate(id=3, priority=0, created_at=dt(10), service_id=1),
        target,
    ]
    assert algorithm.compute_position(target, queue) == 1


def test_position_strict_fifo_same_priority(dt):
    t = dt(30)
    target = Candidate(id=2, priority=0, created_at=t, service_id=1)
    queue = [
        Candidate(id=1, priority=0, created_at=dt(10), service_id=1),
        target,
        Candidate(id=3, priority=0, created_at=dt(50), service_id=1),
    ]
    assert algorithm.compute_position(target, queue) == 2


def test_position_all_priorities_different(dt):
    target = Candidate(id=4, priority=10, created_at=dt(0), service_id=1)
    queue = [
        Candidate(id=1, priority=30, created_at=dt(0), service_id=1),
        Candidate(id=2, priority=20, created_at=dt(0), service_id=1),
        target,
        Candidate(id=3, priority=0,  created_at=dt(0), service_id=1),
    ]
    assert algorithm.compute_position(target, queue) == 3


def test_eta_next_in_line(dt):
    assert algorithm.compute_eta(position=1, avg_minutes=5, active_windows=1) == 0


def test_eta_basic_one_window(dt):
    assert algorithm.compute_eta(position=3, avg_minutes=5, active_windows=1) == 10


def test_eta_two_windows_halves_wait(dt):
    """3-й, 5 мин, 2 окна → 5 минут."""
    assert algorithm.compute_eta(position=3, avg_minutes=5, active_windows=2) == 5


def test_eta_zero_windows_does_not_crash(dt):
    assert algorithm.compute_eta(position=3, avg_minutes=5, active_windows=0) == 10


def test_eta_negative_windows_does_not_crash(dt):
    assert algorithm.compute_eta(position=3, avg_minutes=5, active_windows=-3) == 10


def test_eta_zero_position_clamps_to_one(dt):
    assert algorithm.compute_eta(position=0, avg_minutes=5, active_windows=1) == 0


def test_eta_negative_position_clamps(dt):
    assert algorithm.compute_eta(position=-5, avg_minutes=5, active_windows=1) == 0


def test_eta_zero_avg_minutes(dt):
    assert algorithm.compute_eta(position=5, avg_minutes=0, active_windows=1) == 0


def test_eta_negative_avg_minutes(dt):
    assert algorithm.compute_eta(position=5, avg_minutes=-10, active_windows=1) == 0


@pytest.mark.parametrize(
    "position,avg,windows,expected",
    [
        (1,  10, 1, 0),
        (2,  10, 1, 10),
        (5,  10, 1, 40),
        (5,  10, 2, 20),
        (10, 10, 5, 18),
        (2,  3,  1, 3),
    ],
)
def test_eta_table(position, avg, windows, expected):
    assert algorithm.compute_eta(position, avg, windows) == expected