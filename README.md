# Mantenedor de Calificaciones Tributarias

Sistema web para que un **corredor de bolsa** registre los montos de dividendos que recibe de las empresas y los convierta en **factores de calificación tributaria**, manteniendo el historial completo y trazable.

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white&style=flat)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?logo=fastapi&logoColor=white&style=flat)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black&style=flat)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6-646CFF?logo=vite&logoColor=white&style=flat)](https://vitejs.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white&style=flat)](https://www.sqlite.org/)

---

## Descripción

Los corredores de bolsa reciben cada año la información tributaria de las empresas en **PDF sin formato estándar**. Eso hace imposible automatizar la lectura, por lo que los datos deben ingresarse manualmente y convertirse en factores.

Este sistema ordena ese proceso: **ingreso manual de montos, cálculo automático de factores, carga masiva por CSV, prioridad local del corredor y auditoría completa** de cada operación.

Proyecto del ramo **Proyecto Integrado** (INACAP), basado en un requerimiento real de la empresa **nuam** — el holding que une las bolsas de Santiago, Lima y Colombia.

## Características

- **Mantenedor** con filtros por mercado (acciones, CFI, fondos mutuos), origen y período comercial
- **Ingreso manual** de calificaciones con 29 campos de montos
- **Cálculo automático** de factores (columnas 8 a 37, redondeo a 8 decimales)
- **Carga masiva CSV** de montos (DJ 1948) o factores, con actualización por llave si el registro ya existe
- **Prioridad del corredor**: la información local nunca altera la de la Bolsa
- **Auditoría** de ingreso, modificación y eliminación (log con fecha y hora)

## Stack tecnológico

| Capa | Tecnología | Rol |
|------|-----------|-----|
| Frontend | React + Vite | Interfaz: grilla, formularios, carga de archivos |
| Backend | Python + FastAPI | API REST y reglas de negocio |
| Base de datos | SQLite | Almacenamiento local, sin instalación |

## Requisitos previos

- Python 3.12 o superior
- Node.js 20 o superior
- npm

## Instalación

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Abrir [http://localhost:5173](http://localhost:5173). La API queda en `http://localhost:8000/api`.

## Uso

1. **Ingresar calificación**: completar datos básicos (mercado, instrumento, fecha, secuencia) y los 29 campos de montos.
2. **Calcular**: el sistema convierte los montos en factores (validación: suma de factores 8-19 ≤ 1).
3. **Cargar CSV**: subir archivo con montos o factores; los registros existentes se actualizan por llave (ejercicio + mercado + instrumento + fecha + secuencia + dividendo + tipo sociedad).
4. **Auditoría**: pestaña con el log de todas las operaciones.

## Estructura del proyecto

```
mantenedor/
├── backend/
│   └── app/
│       ├── main.py       →  API (rutas)
│       ├── servicio.py   →  lógica de negocio (CRUD, CSV, auditoría)
│       ├── reglas.py     →  reglas del HDU (cálculo de factores)
│       └── db.py         →  base de datos SQLite
├── frontend/
│   └── src/
│       ├── App.jsx       →  pantalla principal
│       ├── api.js        →  comunicación con el backend
│       └── columnas.js   →  nombres de los 30 factores
└── README.md
```

## Fuentes

- `HDU_Inacap.xlsx` — Historias de Usuario del cliente (nuam): objetivo, alcance, historias, tipos de datos, homologación, formato CSV y flujo de proceso.
- `Apunte_Proyecto_Integrado.md` — resumen del ramo: metodología, contexto de nuam y análisis completo del HDU.

## Estado del proyecto

- [x] Backend: CRUD, cálculo de factores, carga CSV, auditoría
- [x] Frontend: grilla, filtros, formulario, detalle, carga CSV
- [x] Validaciones de negocio (suma ≤ 1, 8 decimales)
- [ ] Módulo RAG (asistente de preguntas) — siguiente paso
- [ ] Pruebas automatizadas — siguiente paso

## Licencia

Proyecto académico — ramo Proyecto Integrado, INACAP 2026.
