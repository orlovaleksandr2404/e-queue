from src.schemas.algorithm import Candidate, NextTicketResponse


def _sort_key(c: Candidate) -> tuple:
    return (-c.priority, c.created_at, c.id)


def select_next(
    candidates: list[Candidate],
    window_service_ids: list[int] | None = None,
) -> NextTicketResponse:
    if not candidates:
        return NextTicketResponse(ticket_id=None, reason="none_available")

    pool = candidates
    if window_service_ids:
        pool = [c for c in pool if c.service_id in window_service_ids]
        if not pool:
            return NextTicketResponse(ticket_id=None, reason="none_available")

    winner = min(pool, key=_sort_key)
    reason = "priority" if winner.priority > 0 else "fifo"
    return NextTicketResponse(ticket_id=winner.id, reason=reason)


def compute_position(target: Candidate, queue: list[Candidate]) -> int:
    t_key = (target.priority, -target.created_at.timestamp(), -target.id)
    ahead = 0
    for c in queue:
        if c.id == target.id:
            continue
        c_key = (c.priority, -c.created_at.timestamp(), -c.id)
        if c_key > t_key:
            ahead += 1
    return ahead + 1


def compute_eta(position: int, avg_minutes: int, active_windows: int = 1) -> int:
    position = max(1, position)
    active_windows = max(1, active_windows)
    avg_minutes = max(0, avg_minutes)

    ahead = position - 1
    if ahead == 0 or avg_minutes == 0:
        return 0

    return max(0, int(round(ahead * avg_minutes / active_windows)))