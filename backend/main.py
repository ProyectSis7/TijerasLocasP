from contextlib import asynccontextmanager
from datetime import date, timedelta
from typing import Optional
import aiosqlite
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB_PATH = "./tijeras_locas.db"

async def startup_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("""CREATE TABLE IF NOT EXISTS barbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'Barbero')""")
        await db.execute("""CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, description TEXT,
            price REAL NOT NULL, duration_min INTEGER NOT NULL DEFAULT 30)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL, client_email TEXT,
            barber_id INTEGER NOT NULL, service_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL, appointment_time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'confirmed')""")
        async with db.execute("SELECT COUNT(*) as c FROM barbers") as cur:
            if (await cur.fetchone())["c"] == 0:
                await db.execute("INSERT INTO barbers (name,role) VALUES ('Andrés','Master')")
                await db.execute("INSERT INTO barbers (name,role) VALUES ('Marcos','Senior')")
                await db.execute("INSERT INTO barbers (name,role) VALUES ('Diego','Style Expert')")
        async with db.execute("SELECT COUNT(*) as c FROM services") as cur:
            if (await cur.fetchone())["c"] == 0:
                await db.execute("INSERT INTO services (name,description,price,duration_min) VALUES ('Corte de pelo','Corte clásico o moderno.',20000,30)")
                await db.execute("INSERT INTO services (name,description,price,duration_min) VALUES ('Barba','Perfilado y toalla caliente.',15000,20)")
                await db.execute("INSERT INTO services (name,description,price,duration_min) VALUES ('Combo','Corte y barba premium.',30000,50)")
        async with db.execute("SELECT COUNT(*) as c FROM appointments") as cur:
            if (await cur.fetchone())["c"] == 0:
                today = date.today()
                citas = [
                    ("Carlos Mendoza",1,1,(today-timedelta(days=6)).isoformat(),"09:00","confirmed"),
                    ("Elena Gómez",2,2,(today-timedelta(days=6)).isoformat(),"11:00","confirmed"),
                    ("Ricardo Silva",1,3,(today-timedelta(days=5)).isoformat(),"10:00","confirmed"),
                    ("Luis Torres",3,1,(today-timedelta(days=4)).isoformat(),"12:00","confirmed"),
                    ("Pedro Martínez",1,2,(today-timedelta(days=3)).isoformat(),"09:30","confirmed"),
                    ("Juan García",2,3,(today-timedelta(days=2)).isoformat(),"15:00","confirmed"),
                    ("Miguel Ruiz",3,1,(today-timedelta(days=1)).isoformat(),"11:00","confirmed"),
                    ("Marcelo Díaz",2,1,today.isoformat(),"10:30","confirmed"),
                    ("Pablo Fernández",1,1,today.isoformat(),"17:30","pending"),
                ]
                for c in citas:
                    await db.execute("INSERT INTO appointments (client_name,barber_id,service_id,appointment_date,appointment_time,status) VALUES (?,?,?,?,?,?)",c)
        await db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_db()
    yield

app = FastAPI(title="Tijeras Locas API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db

class AppointmentCreate(BaseModel):
    client_name: str
    client_email: Optional[str] = None
    barber_id: int
    service_id: int
    appointment_date: str
    appointment_time: str
    status: Optional[str] = "confirmed"

@app.get("/barbers")
async def list_barbers(db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT * FROM barbers ORDER BY id") as cur:
        return [dict(r) for r in await cur.fetchall()]

@app.get("/services")
async def list_services(db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT * FROM services ORDER BY id") as cur:
        return [dict(r) for r in await cur.fetchall()]

@app.post("/appointments", status_code=201)
async def create_appointment(payload: AppointmentCreate, db: aiosqlite.Connection = Depends(get_db)):
    await db.execute("INSERT INTO appointments (client_name,client_email,barber_id,service_id,appointment_date,appointment_time,status) VALUES (?,?,?,?,?,?,?)",
        (payload.client_name,payload.client_email,payload.barber_id,payload.service_id,payload.appointment_date,payload.appointment_time,payload.status))
    await db.commit()
    async with db.execute("SELECT * FROM appointments WHERE id=last_insert_rowid()") as cur:
        return dict(await cur.fetchone())

@app.get("/appointments/analytics")
async def get_analytics(db: aiosqlite.Connection = Depends(get_db)):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    async with db.execute("""SELECT b.id,b.name,b.role,COUNT(a.id) AS total_appointments,
        COALESCE(SUM(s.price),0) AS total_revenue FROM barbers b
        LEFT JOIN appointments a ON a.barber_id=b.id AND a.appointment_date BETWEEN ? AND ? AND a.status!='cancelled'
        LEFT JOIN services s ON s.id=a.service_id GROUP BY b.id ORDER BY total_revenue DESC""",
        (week_start.isoformat(),week_end.isoformat())) as cur:
        barbers = [dict(r) for r in await cur.fetchall()]
    max_rev = max((b["total_revenue"] for b in barbers),default=1) or 1
    for b in barbers:
        b["revenue_pct"] = round(b["total_revenue"]/max_rev*100,1)
    async with db.execute("""SELECT s.id,s.name,s.price,COUNT(a.id) AS total_booked FROM services s
        LEFT JOIN appointments a ON a.service_id=s.id AND a.appointment_date BETWEEN ? AND ? AND a.status!='cancelled'
        GROUP BY s.id ORDER BY total_booked DESC""",(week_start.isoformat(),week_end.isoformat())) as cur:
        services = [dict(r) for r in await cur.fetchall()]
    total_all = sum(s["total_booked"] for s in services) or 1
    for s in services:
        s["pct"] = round(s["total_booked"]/total_all*100,1)
    async with db.execute("""SELECT a.id,a.client_name,a.appointment_time,a.status,
        b.name AS barber_name,s.name AS service_name,s.duration_min FROM appointments a
        JOIN barbers b ON b.id=a.barber_id JOIN services s ON s.id=a.service_id
        WHERE a.appointment_date=? ORDER BY a.appointment_time""",(today.isoformat(),)) as cur:
        today_apts = [dict(r) for r in await cur.fetchall()]
    gaps = []
    for i in range(len(today_apts)-1):
        h1,m1 = map(int,today_apts[i]["appointment_time"].split(":"))
        end = h1*60+m1+today_apts[i]["duration_min"]
        h2,m2 = map(int,today_apts[i+1]["appointment_time"].split(":"))
        start = h2*60+m2
        if start-end >= 60:
            gaps.append({"from":f"{end//60:02d}:{end%60:02d}","to":f"{start//60:02d}:{start%60:02d}","gap_minutes":start-end})
    return {
        "kpis":{"weekly_revenue":sum(b["total_revenue"] for b in barbers),"total_today":len(today_apts),
            "pending_today":sum(1 for a in today_apts if a["status"]=="pending"),"gap_alerts":len(gaps),
            "week_start":week_start.isoformat(),"week_end":week_end.isoformat(),"today":today.isoformat()},
        "barber_ranking":barbers,"service_ranking":services,
        "today_schedule":{"appointments":today_apts,"gaps":gaps}}

@app.get("/appointments")
async def list_appointments(db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT * FROM appointments ORDER BY appointment_date,appointment_time") as cur:
        return [dict(r) for r in await cur.fetchall()]
