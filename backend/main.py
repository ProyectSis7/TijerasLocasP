# ============================================================
#  Tijeras Locas · backend/main.py
#  FastAPI + SQLite (swappable a PostgreSQL con 1 línea)
# ============================================================
#
#  Dependencias (requirements.txt):
#    fastapi==0.111.0
#    uvicorn[standard]==0.29.0
#    aiosqlite==0.20.0       ← driver async para SQLite
#    python-dotenv==1.0.1
#
#  Arranque local:
#    uvicorn main:app --reload --port 8000
#
#  Variables de entorno (.env):
#    DATABASE_URL=sqlite+aiosqlite:///./tijeras_locas.db
#    # Para PostgreSQL:
#    # DATABASE_URL=postgresql+asyncpg://user:pass@host/db
# ============================================================

import os
from datetime import date, time, datetime, timedelta
from typing import Optional, List

import aiosqlite
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

# ── Configuración ─────────────────────────────────────────────
DB_PATH = os.getenv("DB_PATH", "./tijeras_locas.db")
INIT_SQL = os.getenv("INIT_SQL_PATH", "./init.sql")

app = FastAPI(
    title="Tijeras Locas API",
    description="Backend de reservas para la barbería Tijeras Locas",
    version="1.0.0",
)

# Permite llamadas desde el frontend (ajusta origins en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Inicialización de la BD ───────────────────────────────────
async def get_db():
    """Dependencia que devuelve una conexión abierta a SQLite."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row  # filas como diccionarios
        yield db


@app.on_event("startup")
async def startup():
    """Crea las tablas e inserta seed data la primera vez."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Habilitar claves foráneas en SQLite
        await db.execute("PRAGMA foreign_keys = ON")

        # Ejecutar init.sql si las tablas no existen aún
        try:
            with open(INIT_SQL, "r", encoding="utf-8") as f:
                sql = f.read()
            # Separar y ejecutar cada sentencia individualmente
            statements = [s.strip() for s in sql.split(";") if s.strip()]
            for stmt in statements:
                # Ignorar comentarios puros
                if stmt.startswith("--"):
                    continue
                try:
                    await db.execute(stmt)
                except Exception:
                    pass  # Ignora errores de "already exists" en seed data
            await db.commit()
        except FileNotFoundError:
            # Si el archivo SQL no se encuentra, las tablas deben existir ya
            pass


# ── Modelos Pydantic ──────────────────────────────────────────

class AppointmentCreate(BaseModel):
    """Payload para crear una cita."""
    client_name: str
    client_email: Optional[str] = None
    barber_id: int
    service_id: int
    appointment_date: date          # formato: "2024-06-15"
    appointment_time: str           # formato: "10:00"
    status: Optional[str] = "confirmed"


class AppointmentOut(AppointmentCreate):
    id: int
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


# ── Endpoints ─────────────────────────────────────────────────

# ── POST /appointments ────────────────────────────────────────
@app.post("/appointments", response_model=AppointmentOut, status_code=201)
async def create_appointment(
    payload: AppointmentCreate,
    db: aiosqlite.Connection = Depends(get_db),
):
    """
    Crea una nueva cita.
    Valida que el barbero y el servicio existan antes de insertar.
    """
    # Validar barbero
    async with db.execute("SELECT id FROM barbers WHERE id = ?", (payload.barber_id,)) as cur:
        if not await cur.fetchone():
            raise HTTPException(status_code=404, detail="Barbero no encontrado")

    # Validar servicio
    async with db.execute("SELECT id FROM services WHERE id = ?", (payload.service_id,)) as cur:
        if not await cur.fetchone():
            raise HTTPException(status_code=404, detail="Servicio no encontrado")

    # Insertar cita
    await db.execute(
        """
        INSERT INTO appointments
            (client_name, client_email, barber_id, service_id,
             appointment_date, appointment_time, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.client_name,
            payload.client_email,
            payload.barber_id,
            payload.service_id,
            payload.appointment_date.isoformat(),
            payload.appointment_time,
            payload.status,
        ),
    )
    await db.commit()

    # Recuperar el registro recién creado
    async with db.execute("SELECT * FROM appointments WHERE id = last_insert_rowid()") as cur:
        row = await cur.fetchone()

    return dict(row)


# ── GET /appointments/analytics ───────────────────────────────
@app.get("/appointments/analytics")
async def get_analytics(db: aiosqlite.Connection = Depends(get_db)):
    """
    Devuelve tres bloques de información para el dashboard:

    1. barber_ranking   → barberos ordenados por ingresos generados esta semana
    2. service_ranking  → popularidad de servicios (cantidad y % del total)
    3. today_schedule   → agenda de hoy: citas confirmadas + huecos vacíos detectados
    """

    today = date.today()
    # Inicio de la semana actual (lunes)
    week_start = today - timedelta(days=today.weekday())
    week_end   = week_start + timedelta(days=6)

    # ── 1. Ranking de barberos por ingresos esta semana ────────
    async with db.execute(
        """
        SELECT
            b.id,
            b.name,
            b.role,
            COUNT(a.id)         AS total_appointments,
            COALESCE(SUM(s.price), 0) AS total_revenue
        FROM barbers b
        LEFT JOIN appointments a
            ON a.barber_id = b.id
            AND a.appointment_date BETWEEN ? AND ?
            AND a.status != 'cancelled'
        LEFT JOIN services s ON s.id = a.service_id
        GROUP BY b.id, b.name, b.role
        ORDER BY total_revenue DESC
        """,
        (week_start.isoformat(), week_end.isoformat()),
    ) as cur:
        barber_rows = await cur.fetchall()

    barber_ranking = [dict(r) for r in barber_rows]

    # Calcular el máximo para calcular porcentaje de barra en el frontend
    max_revenue = max((b["total_revenue"] for b in barber_ranking), default=1) or 1
    for b in barber_ranking:
        b["revenue_pct"] = round(b["total_revenue"] / max_revenue * 100, 1)

    # ── 2. Ranking de servicios (total de citas en la semana) ──
    async with db.execute(
        """
        SELECT
            s.id,
            s.name,
            s.price,
            COUNT(a.id) AS total_booked
        FROM services s
        LEFT JOIN appointments a
            ON a.service_id = s.id
            AND a.appointment_date BETWEEN ? AND ?
            AND a.status != 'cancelled'
        GROUP BY s.id, s.name, s.price
        ORDER BY total_booked DESC
        """,
        (week_start.isoformat(), week_end.isoformat()),
    ) as cur:
        service_rows = await cur.fetchall()

    total_booked_all = sum(r["total_booked"] for r in service_rows) or 1
    service_ranking = []
    for r in service_rows:
        d = dict(r)
        d["pct"] = round(d["total_booked"] / total_booked_all * 100, 1)
        service_ranking.append(d)

    # ── 3. Agenda de hoy + detección de huecos vacíos ─────────
    async with db.execute(
        """
        SELECT
            a.id,
            a.client_name,
            a.appointment_time,
            a.status,
            b.name  AS barber_name,
            s.name  AS service_name,
            s.duration_min
        FROM appointments a
        JOIN barbers  b ON b.id = a.barber_id
        JOIN services s ON s.id = a.service_id
        WHERE a.appointment_date = ?
        ORDER BY a.appointment_time
        """,
        (today.isoformat(),),
    ) as cur:
        today_rows = await cur.fetchall()

    today_appointments = [dict(r) for r in today_rows]

    # Detectar huecos vacíos entre citas (gaps > 60 min entre fin de una y comienzo de la siguiente)
    gaps = []
    for i in range(len(today_appointments) - 1):
        curr = today_appointments[i]
        nxt  = today_appointments[i + 1]

        # Parsear horas
        h1, m1 = map(int, curr["appointment_time"].split(":"))
        end_curr = h1 * 60 + m1 + curr["duration_min"]

        h2, m2 = map(int, nxt["appointment_time"].split(":"))
        start_next = h2 * 60 + m2

        gap_min = start_next - end_curr
        if gap_min >= 60:
            gaps.append({
                "from": f"{end_curr // 60:02d}:{end_curr % 60:02d}",
                "to":   f"{start_next // 60:02d}:{start_next % 60:02d}",
                "gap_minutes": gap_min,
            })

    # ── KPIs rápidos para las tarjetas superiores ──────────────
    weekly_revenue = sum(b["total_revenue"] for b in barber_ranking)
    total_today    = len(today_appointments)

    # Slots disponibles = huecos de >= 30 min
    async with db.execute(
        """
        SELECT COUNT(*) AS free_slots
        FROM appointments
        WHERE appointment_date = ?
          AND status = 'pending'
        """,
        (today.isoformat(),),
    ) as cur:
        row = await cur.fetchone()
    pending_today = row["free_slots"] if row else 0

    return {
        "kpis": {
            "weekly_revenue":  weekly_revenue,
            "total_today":     total_today,
            "pending_today":   pending_today,
            "gap_alerts":      len(gaps),
            "week_start":      week_start.isoformat(),
            "week_end":        week_end.isoformat(),
            "today":           today.isoformat(),
        },
        "barber_ranking":  barber_ranking,
        "service_ranking": service_ranking,
        "today_schedule": {
            "appointments": today_appointments,
            "gaps":         gaps,
        },
    }


# ── GET /appointments (listado general, útil para debug) ──────
@app.get("/appointments", response_model=List[AppointmentOut])
async def list_appointments(
    date_filter: Optional[str] = None,
    db: aiosqlite.Connection = Depends(get_db),
):
    """Devuelve todas las citas, opcionalmente filtradas por fecha (YYYY-MM-DD)."""
    if date_filter:
        async with db.execute(
            "SELECT * FROM appointments WHERE appointment_date = ? ORDER BY appointment_time",
            (date_filter,),
        ) as cur:
            rows = await cur.fetchall()
    else:
        async with db.execute(
            "SELECT * FROM appointments ORDER BY appointment_date, appointment_time"
        ) as cur:
            rows = await cur.fetchall()

    return [dict(r) for r in rows]


# ── GET /barbers & /services (necesarios para los selects del frontend) ──
@app.get("/barbers")
async def list_barbers(db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT * FROM barbers ORDER BY id") as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


@app.get("/services")
async def list_services(db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT * FROM services ORDER BY id") as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]
