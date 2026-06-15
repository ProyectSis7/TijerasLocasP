-- ============================================================
--  Tijeras Locas Â· init.sql
--  DDL + Seed Data
--  Compatible con PostgreSQL y SQLite (se indican diferencias)
-- ============================================================

-- -----------------------------------------------------------
-- 1. TABLA: barbers
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS barbers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,   -- PostgreSQL: SERIAL PRIMARY KEY
    name        TEXT    NOT NULL,
    role        TEXT    NOT NULL DEFAULT 'Barbero',  -- 'Master', 'Senior', 'Style Expert'
    avatar_url  TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------
-- 2. TABLA: services
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS services (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    description TEXT,
    price       REAL    NOT NULL,
    duration_min INTEGER NOT NULL DEFAULT 30,        -- duraciÃ³n estimada en minutos
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------
-- 3. TABLA: appointments
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS appointments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name     TEXT    NOT NULL,
    client_email    TEXT,
    barber_id       INTEGER NOT NULL REFERENCES barbers(id),
    service_id      INTEGER NOT NULL REFERENCES services(id),
    appointment_date DATE    NOT NULL,               -- YYYY-MM-DD
    appointment_time TIME    NOT NULL,               -- HH:MM
    status          TEXT    NOT NULL DEFAULT 'confirmed',  -- confirmed | pending | cancelled
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
--  SEED DATA
-- ============================================================

-- -----------------------------------------------------------
-- Barberos
-- -----------------------------------------------------------
INSERT INTO barbers (name, role, avatar_url) VALUES
    ('AndrÃ©s',    'Master',       NULL),
    ('Marcos',    'Senior',       NULL),
    ('Diego',     'Style Expert', NULL);

-- -----------------------------------------------------------
-- Servicios
-- -----------------------------------------------------------
INSERT INTO services (name, description, price, duration_min) VALUES
    ('Corte de pelo', 'Corte clÃ¡sico o moderno con acabado a navaja.',            20.00, 30),
    ('Barba',         'Perfilado, rebaje y ritual de toalla caliente.',            15.00, 20),
    ('Combo',         'Corte completo y arreglo de barba premium.',               30.00, 50);

-- -----------------------------------------------------------
-- Citas ficticias (10 registros)
-- Fechas relativas a la semana actual para que el dashboard
-- muestre datos en tiempo real desde el primer arranque.
-- Ajusta las fechas si usas PostgreSQL con NOW()::DATE.
-- -----------------------------------------------------------

-- Lunes de esta semana (dÃ­as relativos simulados con fechas fijas)
INSERT INTO appointments (client_name, client_email, barber_id, service_id, appointment_date, appointment_time, status) VALUES
    ('Carlos Mendoza',  'carlos@example.com',  1, 1, date('now', '-6 days'), '09:00', 'confirmed'),
    ('Elena GÃ³mez',     'elena@example.com',   2, 2, date('now', '-6 days'), '11:00', 'confirmed'),
    ('Ricardo Silva',   'ricardo@example.com', 1, 3, date('now', '-5 days'), '10:00', 'confirmed'),
    ('Luis Torres',     'luis@example.com',    3, 1, date('now', '-5 days'), '12:00', 'confirmed'),
    ('Pedro MartÃ­nez',  'pedro@example.com',   1, 2, date('now', '-4 days'), '09:30', 'confirmed'),
    ('Juan GarcÃ­a',     'juan@example.com',    2, 3, date('now', '-4 days'), '15:00', 'confirmed'),
    ('Miguel Ruiz',     'miguel@example.com',  3, 1, date('now', '-3 days'), '11:00', 'confirmed'),
    ('AndrÃ©s LÃ³pez',    'alopez@example.com',  1, 3, date('now', '-2 days'), '14:00', 'confirmed'),
    ('SofÃ­a DÃ­az',      'sofia@example.com',   2, 2, date('now', '-1 days'), '10:30', 'confirmed'),
    ('Pablo FernÃ¡ndez', 'pablo@example.com',   1, 1, date('now'),            '17:30', 'pending');

-- ============================================================
-- NOTAS PARA POSTGRESQL:
-- Reemplaza AUTOINCREMENT â†’ elimÃ­nalo (usa SERIAL o GENERATED ALWAYS AS IDENTITY)
-- Reemplaza date('now', '-N days') â†’ CURRENT_DATE - INTERVAL 'N days'
-- Reemplaza DATETIME â†’ TIMESTAMP
-- ============================================================
