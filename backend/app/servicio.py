"""Servicio: operaciones de negocio del Mantenedor de Calificaciones Tributarias."""
import csv
import io
import sqlite3

from . import reglas
from .db import get_conn, audit


def _fila_a_dict(fila: sqlite3.Row) -> dict:
    d = dict(fila)
    return d


def listar_calificaciones(mercado: str | None = None,
                          origen: str | None = None,
                          periodo: int | None = None) -> list[dict]:
    q = "SELECT * FROM calificaciones WHERE 1=1"
    params: list = []
    if mercado:
        q += " AND mercado = ?"; params.append(mercado)
    if origen:
        q += " AND origen = ?"; params.append(origen)
    if periodo:
        q += " AND ejercicio = ?"; params.append(periodo)
    q += " ORDER BY ejercicio DESC, instrumento, fecha_pago"
    with get_conn() as conn:
        return [_fila_a_dict(r) for r in conn.execute(q, params).fetchall()]


def obtener_calificacion(registro_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM calificaciones WHERE id=?", (registro_id,)).fetchone()
        if not row:
            return None
        montos = {r["columna"]: r["monto"] for r in conn.execute(
            "SELECT columna, monto FROM montos WHERE calificacion_id=?", (registro_id,))}
        factores = {r["columna"]: r["factor"] for r in conn.execute(
            "SELECT columna, factor FROM factores WHERE calificacion_id=?", (registro_id,))}
        d = _fila_a_dict(row)
        d["montos"] = montos
        d["factores"] = factores
        return d


def _insertar_calificacion(conn, data: dict, fuente: str) -> int:
    cur = conn.execute(
        """INSERT INTO calificaciones
           (ejercicio, mercado, instrumento, fecha_pago, secuencia,
            numero_dividendo, tipo_sociedad, valor_historico, isfut, origen, fuente)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (data["ejercicio"], data["mercado"], data["instrumento"], data["fecha_pago"],
         data["secuencia"], data["numero_dividendo"], data["tipo_sociedad"],
         data["valor_historico"], data.get("isfut", 0), data.get("origen", "corredor"),
         fuente),
    )
    rid = cur.lastrowid
    for c in reglas.COLUMNAS_MONTOS:
        if c in (data.get("montos") or {}):
            conn.execute("INSERT OR REPLACE INTO montos VALUES (?,?,?)",
                         (rid, c, data["montos"][c]))
    for c in reglas.COLUMNAS_FACTORES:
        if c in (data.get("factores") or {}):
            conn.execute("INSERT OR REPLACE INTO factores VALUES (?,?,?)",
                         (rid, c, data["factores"][c]))
    return rid


def crear_calificacion(data: dict, fuente: str = "manual") -> dict:
    """Crear calificacion. Si data trae montos sin factores -> calcula factores."""
    montos = data.get("montos") or {}
    factores = data.get("factores")
    if factores is None and montos:
        factores = reglas.calcular_factores(montos)
        reglas.validar_suma_factores(factores)
    if factores:
        reglas.validar_suma_factores(factores)
    if factores is not None:
        data["factores"] = factores  # inyecta para que _insertar los persista
    with get_conn() as conn:
        rid = _insertar_calificacion(conn, data, fuente)
        audit(conn, "INSERT", rid, f"{data['mercado']} {data['instrumento']} ej{data['ejercicio']}")
    return obtener_calificacion(rid)


def modificar_calificacion(registro_id: int, data: dict) -> dict | None:
    montos = data.get("montos")
    factores = data.get("factores")
    if factores is None and montos:
        factores = reglas.calcular_factores(montos)
        reglas.validar_suma_factores(factores)
    if factores:
        reglas.validar_suma_factores(factores)
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM calificaciones WHERE id=?", (registro_id,)).fetchone()
        if not row:
            return None
        campos = {k: v for k, v in data.items()
                  if k in ("ejercicio", "mercado", "instrumento", "fecha_pago",
                           "secuencia", "numero_dividendo", "tipo_sociedad",
                           "valor_historico", "isfut", "origen", "fuente")}
        for k, v in campos.items():
            conn.execute(f"UPDATE calificaciones SET {k}=?, fecha_modificacion=datetime('now','localtime') WHERE id=?",
                         (v, registro_id))
        if montos:
            for c, v in montos.items():
                conn.execute("INSERT OR REPLACE INTO montos VALUES (?,?,?)", (registro_id, int(c), v))
        if factores:
            for c, v in factores.items():
                conn.execute("INSERT OR REPLACE INTO factores VALUES (?,?,?)", (registro_id, int(c), v))
        audit(conn, "UPDATE", registro_id, f"modificacion id={registro_id}")
    return obtener_calificacion(registro_id)


def eliminar_calificacion(registro_id: int) -> bool:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM calificaciones WHERE id=?", (registro_id,)).fetchone()
        if not row:
            return False
        conn.execute("DELETE FROM calificaciones WHERE id=?", (registro_id,))
        audit(conn, "DELETE", registro_id, f"eliminacion id={registro_id}")
    return True


def calcular_por_registro(registro_id: int) -> dict | None:
    """Recalcula los factores de una calificacion a partir de sus montos (boton Calcular)."""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM calificaciones WHERE id=?", (registro_id,)).fetchone()
        if not row:
            return None
        montos = {r["columna"]: r["monto"] for r in conn.execute(
            "SELECT columna, monto FROM montos WHERE calificacion_id=?", (registro_id,))}
        factores = reglas.calcular_factores(montos)
        reglas.validar_suma_factores(factores)
        for c, v in factores.items():
            conn.execute("INSERT OR REPLACE INTO factores VALUES (?,?,?)", (registro_id, int(c), v))
        audit(conn, "CALCULAR", registro_id, "recalculo de factores")
    return obtener_calificacion(registro_id)


def _llave(data: dict) -> tuple:
    return tuple(str(data[k]).strip() for k in reglas.LLAVE_CAMPOS)


def cargar_csv(texto: str, tipo: str = "montos") -> dict:
    """Carga masiva CSV (historia 10): actualiza por llave si existe, agrega si no.

    tipo='montos': usa montos del CSV y calcula factores.
    tipo='factores': usa factores del CSV directamente.
    Devuelve {insertados, actualizados, errores}.
    """
    if tipo not in ("montos", "factores"):
        raise ValueError("tipo debe ser 'montos' o 'factores'")
    reader = csv.DictReader(io.StringIO(texto))
    if not reader.fieldnames:
        raise ValueError("El archivo CSV no tiene encabezados.")
    insertados = actualizados = 0
    errores = []
    llave_existente = {}
    with get_conn() as conn:
        # Cargar llaves existentes
        for r in conn.execute("SELECT * FROM calificaciones"):
            llave = tuple(str(r[k]).strip() if r[k] is not None else "" for k in reglas.LLAVE_CAMPOS)
            llave_existente[llave] = r["id"]
        for i, fila in enumerate(reader, start=2):
            try:
                data = reglas.mapear_fila_csv(fila)
            except Exception as e:
                errores.append(f"fila {i}: {e}")
                continue
            if tipo == "montos":
                factores = reglas.calcular_factores(data["montos"])
                reglas.validar_suma_factores(factores)
                data["factores"] = factores
            else:
                reglas.validar_suma_factores(data["factores"])
            llave = _llave(data)
            if llave in llave_existente:
                rid = llave_existente[llave]
                conn.execute(
                    """UPDATE calificaciones SET mercado=?, instrumento=?, valor_historico=?,
                       isfut=?, fuente='archivo', fecha_modificacion=datetime('now','localtime')
                       WHERE id=?""",
                    (data["mercado"], data["instrumento"], data["valor_historico"],
                     data["isfut"], rid))
                for c, v in data["montos"].items():
                    conn.execute("INSERT OR REPLACE INTO montos VALUES (?,?,?)", (rid, c, v))
                for c, v in data["factores"].items():
                    conn.execute("INSERT OR REPLACE INTO factores VALUES (?,?,?)", (rid, c, v))
                audit(conn, "CARGA", rid, f"actualizado por llave (csv {tipo}) fila {i}")
                actualizados += 1
            else:
                rid = _insertar_calificacion(conn, data, "archivo")
                llave_existente[llave] = rid
                audit(conn, "CARGA", rid, f"insertado (csv {tipo}) fila {i}")
                insertados += 1
    return {"insertados": insertados, "actualizados": actualizados, "errores": errores}


def listar_auditoria(limite: int = 100) -> list[dict]:
    with get_conn() as conn:
        return [_fila_a_dict(r) for r in conn.execute(
            "SELECT * FROM auditoria ORDER BY id DESC LIMIT ?", (limite,)).fetchall()]
