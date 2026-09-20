import asyncio
from sqlalchemy import select
from src.core.database import AsyncSessionLocal
from src.core.security import hash_password
from src.models.user import User, UserRole
from src.models.organization import Organization
from src.models.service import Service
from src.models.window import Window

async def seed():
    async with AsyncSessionLocal() as db:
        print("Инициализация демонстрационных данных")

        # 1. Администратор
        admin_res = await db.execute(select(User).where(User.username == "admin"))
        if not admin_res.scalar_one_or_none():
            admin = User(
                username="admin",
                hashed_password=hash_password("adminpassword"),
                full_name="Главный Администратор",
                role=UserRole.ADMIN,
            )
            db.add(admin)
            print("Создан администратор: admin / adminpassword")

        # 2. Оператор
        op_res = await db.execute(select(User).where(User.username == "operator1"))
        if not op_res.scalar_one_or_none():
            op = User(
                username="operator1",
                hashed_password=hash_password("secretpassword"),
                full_name="Иванов Иван",
                role=UserRole.OPERATOR,
            )
            db.add(op)
            print("Создан оператор: operator1 / secretpassword")

        # 3. Организация
        org_res = await db.execute(select(Organization).where(Organization.name == "Центральное отделение"))
        if not org_res.scalar_one_or_none():
            org = Organization(name="Центральное отделение", address="ул. Ленина, д. 10")
            db.add(org)
            print("Создана организация: Центральное отделение")

        # 4. Услуги
        svc_a_res = await db.execute(select(Service).where(Service.prefix == "A"))
        svc_a = svc_a_res.scalar_one_or_none()
        if not svc_a:
            svc_a = Service(name="Оформление карты", prefix="A", avg_duration_minutes=10)
            db.add(svc_a)
            print("Создана услуга: [A] Оформление карты")

        svc_b_res = await db.execute(select(Service).where(Service.prefix == "B"))
        svc_b = svc_b_res.scalar_one_or_none()
        if not svc_b:
            svc_b = Service(name="Кредитование", prefix="B", avg_duration_minutes=20)
            db.add(svc_b)
            print("Создана услуга: [B] Кредитование")

        await db.flush()

        # 5. Окно
        win_res = await db.execute(select(Window).where(Window.number == 1))
        win = win_res.scalar_one_or_none()
        if not win:
            win = Window(number=1, name="Окно №1")
            win.services = [svc_a, svc_b]
            db.add(win)
            print("Создано Окно №1 со списком услуг [A, B]")

        await db.commit()
        print("Наполнение базы данных успешно завершено")

if __name__ == "__main__":
    asyncio.run(seed())
