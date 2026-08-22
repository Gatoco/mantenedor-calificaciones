# Verificación SDD (liviana) — Mantenedor de Calificaciones Tributarias

> Fecha: 2026-08-22 · Modo: `none` · Nivel: entrega de idea al profe

## Entregables

| Entregable | Estado |
|-----------|--------|
| `mantenedor/README.md` | ✅ OK — 70% del esfuerzo, lenguaje simple, al grano |
| `backend/` (app: db, reglas, servicio, main) | ✅ OK — importa, 12 rutas API |
| `frontend/` (App, api, columnas, main, styles) | ✅ OK — estructura completa Vite + React |
| `requirements.txt` / `package.json` | ✅ OK |

## Código (30%)

- CRUD de calificaciones con llave de negocio (ejercicio+mercado+instrumento+fecha+secuencia+dividendo+tipo)
- Cálculo de factores: `monto / suma(8..19)`, 8 decimales, validación suma ≤ 1
- Carga CSV (montos/factores) con upsert por llave + auditoría
- API en `main.py`, reglas del HDU en `reglas.py`

## Pendientes (no bloqueantes para presentar la idea)

- [ ] Probar E2E en navegador (el puerto 8000 quedó ocupado por un proceso previo; se mató con pkill)
- [ ] Módulo RAG (siguiente iteración)
- [ ] Pruebas automatizadas

## Veredicto

**PASS** — Suficiente para presentar la idea al profe: README claro + código base que ya importa y tiene las funciones centrales.
