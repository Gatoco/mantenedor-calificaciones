"""Business rules from HDU_Inacap.xlsx (hojas 3.TIpos, 3.2 Homologacion, 3.1 Archivo de carga).

Reglas clave:
- Factores: columnas 8..37 (30 factores), decimal redondeado al 8vo decimal, <= 1.
- Calculo: factor_i = monto_i / suma(montos columna 8..19)  (hoja 3.2, fila 9).
- Validacion: suma factores 8..19 <= 1 (pruebas de impacto, hoja 4).
"""
from decimal import Decimal, ROUND_HALF_UP

COLUMNAS_MONTOS = list(range(8, 20))    # 8..19 -> base del calculo (suma)
COLUMNAS_FACTORES = list(range(8, 38))  # 8..37 -> 30 factores
CAMPOS_BASE_CSV = [
    "ejercicio", "mercado", "instrumento", "fecha", "secuencia",
    "numero_dividendo", "tipo_sociedad", "valor_historico",
]
LLAVE_CAMPOS = [
    "ejercicio", "mercado", "instrumento", "fecha", "secuencia",
    "numero_dividendo", "tipo_sociedad",
]


def redondear_8(valor: float) -> float:
    """Redondeo a 8 decimales (hoja 3.TIpos: 'Decimal redondeado al 8vo decimal')."""
    return float(Decimal(str(valor)).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP))


def calcular_factores(montos: dict[int, float]) -> dict[int, float]:
    """factor_i = monto_i / suma(montos 8..19), redondeado a 8 decimales.

    Si la suma es 0 -> todos los factores en 0 (no hay division por cero).
    """
    base = {c: montos.get(c, 0.0) or 0.0 for c in COLUMNAS_MONTOS}
    total = sum(base.values())
    if total == 0:
        return {c: 0.0 for c in COLUMNAS_FACTORES}
    return {c: redondear_8(base.get(c, 0.0) / total) for c in COLUMNAS_FACTORES}


def validar_suma_factores(factores: dict[int, float]) -> None:
    """Regla del HDU: la suma de los factores 8..19 debe ser <= 1."""
    suma = sum(factores.get(c, 0.0) or 0.0 for c in COLUMNAS_MONTOS)
    if suma > 1.00000001:
        raise ValueError(
            f"La suma de los factores de la columna 8 a la 19 es {suma:.8f} y no puede superar 1."
        )


def normalizar_fecha(valor: str) -> str:
    """Acepta '2023-12-12', '12-12-2023', '2023-12-12 00:00:00' -> ISO YYYY-MM-DD."""
    v = valor.strip()
    if v[:10] and v[4:5] == "-" and len(v) >= 10:
        return v[:10]
    partes = v.split(" ")[0].split("-")
    if len(partes) == 3 and len(partes[2]) == 4:
        return f"{partes[2]}-{partes[1]}-{partes[0]}"
    raise ValueError(f"Formato de fecha no reconocido: {valor!r}")


def mapear_fila_csv(fila: dict) -> dict:
    """Mapea una fila del CSV (encabezados de la hoja 3.1) a los campos del modelo."""
    fecha = normalizar_fecha(str(fila.get("fecha", "")))
    montos = {}
    for c in COLUMNAS_MONTOS:
        k = f"monto_{c}"
        montos[c] = float(fila.get(k, 0.0) or 0.0)
    factores = {}
    for c in COLUMNAS_FACTORES:
        k = f"factor_{c}"
        factores[c] = float(fila.get(k, 0.0) or 0.0)
    return {
        "ejercicio": int(fila["ejercicio"]),
        "mercado": str(fila["mercado"]).strip(),
        "instrumento": str(fila["instrumento"]).strip(),
        "fecha": fecha,
        "secuencia": int(fila["secuencia"]),
        "numero_dividendo": int(fila["numero_dividendo"]),
        "tipo_sociedad": str(fila["tipo_sociedad"]).strip().upper(),
        "valor_historico": float(fila.get("valor_historico", 0.0) or 0.0),
        "isfut": 1 if str(fila.get("isfut", "")).strip().upper() in ("1", "TRUE", "S", "SI", "X") else 0,
        "montos": montos,
        "factores": factores,
    }
