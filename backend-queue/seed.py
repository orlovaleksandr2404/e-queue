import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.database import Base, SessionLocal, engine
from src.models.ticket import Ticket, TicketStatus
from datetime import date

from src.core.database import Base, SessionLocal, engine
from src.models.ticket import Ticket, TicketStatus

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if not db.query(Ticket).first():
    db.add_all([
        Ticket(number="A-001", seq=1, queue_date=date.today(),
               service_id=1, service_name="Справки", service_prefix="A",
               avg_minutes=5, status=TicketStatus.waiting),
        Ticket(number="A-002", seq=2, queue_date=date.today(),
               service_id=1, service_name="Справки", service_prefix="A",
               avg_minutes=5, status=TicketStatus.waiting),
        Ticket(number="B-001", seq=1, queue_date=date.today(),
               service_id=2, service_name="Платежи", service_prefix="B",
               avg_minutes=3, status=TicketStatus.waiting),
    ])
    db.commit()

print("OK. Создано тестовых талонов:", db.query(Ticket).count())
db.close()