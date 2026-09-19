from src.schemas.algorithm import Candidate, NextTicketResponse



def select_next(
    candidates: list[Candidate],
    window_service_ids: list[int] | None = None,
) -> NextTicketResponse:
    pool = candidates
    if window_service_ids:
        pool = [c for c in pool if c.service_id in window_service_ids]

    if not pool:
        return NextTicketResponse(ticket_id=None, reason="none_available")

    pool.sort(key=lambda c: (-c.priority, c.created_at))
    winner = pool[0]

    reason = "priority" if winner.priority > 0 else "fifo"
    return NextTicketResponse(ticket_id=winner.id, reason=reason)



def compute_position(target: Candidate, queue: list[Candidate]) -> int:

    ahead = 0
    t_key = (target.priority, -target.created_at.timestamp())
    for c in queue:
        if c.id == target.id:
            continue
        c_key = (c.priority, -c.created_at.timestamp())
        if c_key > t_key:
            ahead += 1
    return ahead + 1



def compute_eta(position: int, avg_minutes: int, active_windows: int = 1) -> int:
    ahead = max(0, position - 1)
    windows = max(1, active_windows)
    return int(round(ahead * avg_minutes / windows))