"""SQLite schema and connection helpers."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mantenedor.db"

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS calificaciones (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    ejercicio        INTEGER NOT NULL,
    mercado          TEXT    NOT NULL,
    instrumento      TEXT    NOT NULL,
    fecha_pago       TEXT    NOT NULL,          -- ISO YYYY-MM-DD
    secuencia        INTEGER NOT NULL,
    numero_dividendo INTEGER NOT NULL,
    tipo_sociedad    TEXT    NOT NULL CHECK (tipo_sociedad IN ('A','C')),
    valor_historico  REAL    NOT NULL DEFAULT 0,
    isfut            INTEGER NOT NULL DEFAULT 0,
    origen           TEXT    NOT NULL DEFAULT 'corredor'
                     CHECK (origen IN ('corredor','entidad')),
    fuente           TEXT    NOT NULL DEFAULT 'manual'
                     CHECK (fuente IN ('manual','archivo','sistema')),
    fecha_creacion   TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    fecha_modificacion TEXT  NOT NULL DEFAULT (datetime('now','localtime'))
);

-- Llave de negocio (historia 10): actualiza si existe, agrega si no.
CREATE UNIQUE INDEX IF NOT EXISTS uq_calificacion_llave
ON calificaciones (ejercicio, mercado, instrumento, fecha_pago,
                   secuencia, numero_dividendo, tipo_sociedad);

CREATE TABLE IF NOT EXISTS montos (
    calificacion_id INTEGER NOT NULL REFERENCES calificaciones(id) ON DELETE CASCADE,
    columna         INTEGER NOT NULL CHECK (columna BETWEEN 8 AND 37),
    monto           REAL    NOT NULL,
    PRIMARY KEY (calificacion_id, columna)
);

CREATE TABLE IF NOT EXISTS factores (
    calificacion_id INTEGER NOT NULL REFERENCES calificaciones(id) ON DELETE CASCADE,
    columna         INTEGER NOT NULL CHECK (columna BETWEEN 8 AND 37),
    factor          REAL    NOT NULL,
    PRIMARY KEY (calificacion_id, columna)
);

CREATE TABLE IF NOT EXISTS auditoria (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    accion       TEXT NOT NULL,                 -- INSERT / UPDATE / DELETE / CALCULAR / CARGA
    registro_id  INTEGER,
    detalle      TEXT NOT NULL DEFAULT '',
    usuario      TEXT NOT NULL DEFAULT 'corredor',
    fecha        TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
"""


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def audit(conn: sqlite3.Connection, accion: str, registro_id: int | None,
          detalle: str, usuario: str = "corredor") -> None:
    conn.execute(
        "INSERT INTO auditoria (accion, registro_id, detalle, usuario) VALUES (?,?,?,?)",
        (accion, registro_id, detalle, usuario),
    )
