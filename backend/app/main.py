"""API REST del Mantenedor de Calificaciones Tributarias (nuam)."""
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import servicio
from .db import init_db

app = FastAPI(title="Mantenedor de Calificaciones Tributarias", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    init_db()


class CalificacionIn(BaseModel):
    ejercicio: int = Field(ge=2000, le=2100)
    mercado: str = Field(min_length=1, max_length=3)
    instrumento: str = Field(min_length=1, max_length=50)
    fecha_pago: str
    secuencia: int = Field(ge=0)
    numero_dividendo: int = Field(ge=0)
    tipo_sociedad: str = Field(pattern="^[AaCc]$")
    valor_historico: float = 0.0
    isfut: bool = False
    origen: str = Field(default="corredor", pattern="^(corredor|entidad)$")
    montos: dict[int, float] = {}
    factores: dict[int, float] | None = None


class CalificacionUpdate(CalificacionIn):
    ejercicio: int | None = None
    mercado: str | None = None
    instrumento: str | None = None
    fecha_pago: str | None = None
    secuencia: int | None = None
    numero_dividendo: int | None = None
    tipo_sociedad: str | None = None
    valor_historico: float | None = None
    isfut: bool | None = None
    origen: str | None = None


@app.get("/api/calificaciones")
def listar(mercado: str | None = None, origen: str | None = None,
           periodo: int | None = None):
    return servicio.listar_calificaciones(mercado, origen, periodo)


@app.get("/api/calificaciones/{registro_id}")
def obtener(registro_id: int):
    d = servicio.obtener_calificacion(registro_id)
    if not d:
        raise HTTPException(404, "Calificacion no encontrada")
    return d


@app.post("/api/calificaciones", status_code=201)
def crear(data: CalificacionIn):
    return servicio.crear_calificacion(data.model_dump())


@app.put("/api/calificaciones/{registro_id}")
def modificar(registro_id: int, data: CalificacionUpdate):
    d = servicio.modificar_calificacion(registro_id, data.model_dump(exclude_unset=True))
    if not d:
        raise HTTPException(404, "Calificacion no encontrada")
    return d


@app.delete("/api/calificaciones/{registro_id}", status_code=204)
def eliminar(registro_id: int):
    if not servicio.eliminar_calificacion(registro_id):
        raise HTTPException(404, "Calificacion no encontrada")


@app.post("/api/calificaciones/{registro_id}/calcular")
def calcular(registro_id: int):
    d = servicio.calcular_por_registro(registro_id)
    if not d:
        raise HTTPException(404, "Calificacion no encontrada")
    return d


@app.post("/api/carga")
async def carga(archivo: UploadFile = File(...), tipo: str = "montos"):
    contenido = (await archivo.read()).decode("utf-8-sig")
    try:
        return servicio.cargar_csv(contenido, tipo)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/api/auditoria")
def auditoria(limite: int = 100):
    return servicio.listar_auditoria(limite)
