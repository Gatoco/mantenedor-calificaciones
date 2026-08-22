# MANTENEDOR DE CALIFICACIONES TRIBUTARIAS

```
   __  __            __          _                        _          __
  / / / /___  ____  / /__     __(_)_ __   ___ _ __  __   / /   _____/ /_____
 / / / / __ \/ __ \/ / _ \   / / / | '_ \ / _ \ '_ \/ /  / / | / / ___/ __/
/ /_/ / / / / /_/ / /  __/  / / /| | | | |  __/ | | \ \ / /| |/ (__  ) /_
\____/_/ /_/\____/_/\___/  /_/ |_|_| |_|\___|_| |_|\_V_/ |_/ \___/_/  \__/
```

**Sistema web para que un corredor de bolsa registre montos de dividendos
y los convierta en factores de calificación tributaria.**

Proyecto del ramo **Proyecto Integrado** (INACAP), basado en un requerimiento
real de la empresa **nuam** — el holding que une las bolsas de Santiago,
Lima y Colombia.

---

## ¿POR QUÉ EXISTE?

Los corredores reciben cada año la información tributaria de las empresas
en PDFs sin formato estándar. No se puede automatizar la lectura, así que
alguien debe ingresar los datos a mano y convertir montos en factores.
Este sistema ordena ese proceso de principio a fin.

---

## FUNCIONALIDADES

```
┌──────────────────────────────────────────────────────────────────────────┐
│  MANTENEDOR        Grilla con filtros: mercado, origen, período          │
│  INGRESAR          Formulario: datos básicos + 29 campos de montos       │
│  CALCULAR          Convierte montos en factores (suma 8-19 ≤ 1)          │
│  MODIFICAR/ELIMINAR  Edición y borrado con auditoría                     │
│  CARGA CSV         Subida masiva de montos (DJ 1948) o factores          │
│  AUDITORÍA         Log completo de cada operación                        │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## TECNOLOGÍAS

```
  FRONTEND              BACKEND               BASE DE DATOS
  ────────              ───────               ─────────────

  ████████              ████████              ████████
  ██ React              ██ Python             ██ SQLite
  ████████              ████████              ████████
  ██ Vite               ██ FastAPI            ██ Archivo local
  ████████              ████████              ████████
```

| Capa | Tecnología | Rol |
|------|-----------|-----|
| Frontend | React + Vite | Interfaz de usuario (grilla, formularios, carga CSV) |
| Backend | Python + FastAPI | API y reglas de negocio (cálculo, validaciones, auditoría) |
| Datos | SQLite | Almacenamiento local, sin instalación |

**Módulo futuro:** asistente con RAG que responda preguntas sobre el
proyecto usando los documentos del ramo (HDU, transcripciones, README).

---

## CÓMO CORRERLO

### Backend — terminal 1

```bash
cd mantenedor/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --port 8000
```

### Frontend — terminal 2

```bash
cd mantenedor/frontend
npm install
npm run dev
```

Abrir `http://localhost:5173` — la API queda en `http://localhost:8000/api`.

---

## ESTRUCTURA

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

---

## ESTADO

- [x] Backend: CRUD, cálculo de factores, carga CSV, auditoría
- [x] Frontend: grilla, filtros, formulario, detalle, carga CSV
- [x] Validaciones de negocio (suma ≤ 1, 8 decimales)
- [ ] Módulo RAG (asistente) — siguiente paso
- [ ] Pruebas automatizadas — siguiente paso

---

## FUENTES

| Documento | Contenido |
|-----------|-----------|
| `HDU_Inacap.xlsx` | Historias de Usuario de nuam: objetivo, alcance, 10 historias, tipos de datos, homologación, CSV, flujo |
| `Apunte_Proyecto_Integrado.md` | Resumen del ramo: metodología, contexto nuam, análisis del HDU |
| Transcripciones de videos | 2 clases en `.sdd/work/` |
