from fastapi import APIRouter, HTTPException

from src.core import core_client
from src.schemas.algorithm import (
    Candidate, EtaRequest, EtaResponse,
    NextTicketRequest, NextTicketResponse, WaitTimeResponse,
)
from src.services import algorithm

router = APIRouter(prefix="/algorithm", tags=["algorithm"])


@router.post("/next-ticket", response_model=NextTicketResponse)
def next_ticket(req: NextTicketRequest) -> NextTicketResponse:

    return algorithm.select_next(req.candidates, req.window_service_ids or None)


@router.get("/tickets/{ticket_id}/wait-time", response_model=WaitTimeResponse)
async def wait_time(ticket_id: int) -> WaitTimeResponse:
    """
    Queue тянет данные из Core (read-only внутренний API),
    считает позицию и ETA, возвращает Core — тот отдаёт фронту.
    """
    ticket = await core_client.fetch_ticket(ticket_id)
    if ticket.get("status") != "WAITING":
        raise HTTPException(400, "Талон не в статусе ожидания")

    service_id = ticket["service_id"]
    service_name = (ticket.get("service") or {}).get("name", "")
    avg_minutes = (ticket.get("service") or {}).get("avg_duration_minutes", 10)

    waiting_raw = await core_client.fetch_waiting(service_id)
    queue = [
        Candidate(
            id=t["id"],
            priority=t.get("priority", 0),
            created_at=t["created_at"],
            service_id=t["service_id"],
        )
        for t in waiting_raw
    ]
    target = Candidate(
        id=ticket["id"],
        priority=ticket.get("priority", 0),
        created_at=ticket["created_at"],
        service_id=service_id,
    )

    position = algorithm.compute_position(target, queue)
    active_windows = await core_client.count_active_windows(service_id)
    eta = algorithm.compute_eta(position, avg_minutes, active_windows)

    return WaitTimeResponse(
        ticket_id=ticket_id,
        number=ticket["number"],
        service_name=service_name,
        position=position,
        eta_minutes=eta,
    )


@router.post("/eta", response_model=EtaResponse)
def eta(req: EtaRequest) -> EtaResponse:
    return EtaResponse(
        eta_minutes=algorithm.compute_eta(
            req.position, req.avg_minutes, req.active_windows
        )
    )