import React, { useEffect, useState } from 'react'
import { api } from './api.js'
import { LABELS, MONTOS_COLS, BASE_COLS, formatFecha, sumaBase } from './columnas.js'
import './styles.css'

const vacia = () => ({
  ejercicio: new Date().getFullYear(),
  mercado: '',
  instrumento: '',
  fecha_pago: '',
  secuencia: '',
  numero_dividendo: '',
  tipo_sociedad: 'A',
  valor_historico: '',
  isfut: false,
  origen: 'corredor',
  montos: {},
  factores: {},
})

export default function App() {
  const [filtros, setFiltros] = useState({ mercado: '', origen: '', periodo: '' })
  const [filas, setFilas] = useState([])
  const [modal, setModal] = useState(null) // { modo: 'crear'|'editar', id?, form }
  const [detalle, setDetalle] = useState(null)
  const [aviso, setAviso] = useState(null)
  const [cargando, setCargando] = useState(false)
  const [pestana, setPestana] = useState('calificaciones') // calificaciones | auditoria

  async function cargar() {
    setCargando(true)
    try {
      const r = await api.listar(filtros)
      setFilas(r)
    } catch (e) {
      mostrarAviso(e.message, true)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => { cargar() }, [])

  function mostrarAviso(msg, error = false) {
    setAviso({ msg, error })
    setTimeout(() => setAviso(null), 5000)
  }

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>Calificaciones Tributarias</h1>
          <p className="sub">Mantenedor nuam — montos a factores · local por corredor</p>
        </div>
        <nav className="tabs">
          <button className={pestana === 'calificaciones' ? 'tab act' : 'tab'} onClick={() => setPestana('calificaciones')}>Calificaciones</button>
          <button className={pestana === 'auditoria' ? 'tab act' : 'tab'} onClick={() => setPestana('auditoria')}>Auditoría</button>
        </nav>
      </header>

      {aviso && <div className={aviso.error ? 'aviso err' : 'aviso'}>{aviso.msg}</div>}

      {pestana === 'calificaciones' ? (
        <>
          <Filtros filtros={filtros} setFiltros={setFiltros} onBuscar={cargar} />
          <div className="toolbar">
            <button className="btn prim" onClick={() => setModal({ modo: 'crear', form: vacia() })}>Ingresar</button>
            <CargaCsv onResultado={(r) => { cargar(); mostrarAviso(`Carga OK: ${r.insertados} insertados, ${r.actualizados} actualizados${r.errores?.length ? `, ${r.errores.length} errores` : ''}`) }} />
          </div>
          <table className="grilla">
            <thead>
              <tr>
                <th>Ejercicio</th><th>Mercado</th><th>Instrumento</th><th>Fecha pago</th>
                <th>Secuencia</th><th>N° dividendo</th><th>Tipo soc.</th><th>ISFUT</th>
                <th>Origen</th><th>Fuente</th><th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {cargando && <tr><td colSpan={11} className="centro">Cargando…</td></tr>}
              {!cargando && filas.length === 0 && <tr><td colSpan={11} className="centro">Sin calificaciones. Usa «Ingresar» o carga un CSV.</td></tr>}
              {filas.map((f) => (
                <tr key={f.id}>
                  <td>{f.ejercicio}</td><td>{f.mercado}</td><td>{f.instrumento}</td>
                  <td>{formatFecha(f.fecha_pago)}</td><td>{f.secuencia}</td><td>{f.numero_dividendo}</td>
                  <td>{f.tipo_sociedad}</td>
                  <td>{f.isfut ? 'Sí' : ''}</td>
                  <td>{f.origen}</td><td>{f.fuente}</td>
                  <td className="acciones">
                    <button onClick={async () => { setDetalle(await api.obtener(f.id)) }}>Ver</button>
                    <button onClick={() => setModal({ modo: 'editar', id: f.id, form: convertirForm(f) })}>Modificar</button>
                    <button className="peligro" onClick={async () => { if (confirm(`¿Eliminar ${f.instrumento} ej.${f.ejercicio}?`)) { await api.eliminar(f.id); cargar(); mostrarAviso('Eliminada') } }}>Eliminar</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      ) : (
        <Auditoria />
      )}

      {modal && (
        <ModalCalificacion
          modal={modal}
          onClose={() => setModal(null)}
          onGuardado={async (data) => {
            try {
              if (modal.modo === 'crear') await api.crear(data)
              else await api.modificar(modal.id, data)
              setModal(null); cargar(); mostrarAviso(modal.modo === 'crear' ? 'Calificación creada' : 'Calificación modificada')
            } catch (e) { mostrarAviso(e.message, true) }
          }}
        />
      )}

      {detalle && <ModalDetalle detalle={detalle} onClose={() => setDetalle(null)}
        onCalcular={async () => {
          try { setDetalle(await api.calcular(detalle.id)); cargar(); mostrarAviso('Factores recalculados') }
          catch (e) { mostrarAviso(e.message, true) }
        }} />}
    </div>
  )
}

function Filtros({ filtros, setFiltros, onBuscar }) {
  return (
    <div className="filtros">
      <label>Mercado
        <select value={filtros.mercado} onChange={(e) => setFiltros({ ...filtros, mercado: e.target.value })}>
          <option value="">Todos</option><option>ACN</option><option>CFI</option><option>FM</option>
        </select>
      </label>
      <label>Origen
        <select value={filtros.origen} onChange={(e) => setFiltros({ ...filtros, origen: e.target.value })}>
          <option value="">Todos</option><option>corredor</option><option>entidad</option>
        </select>
      </label>
      <label>Período comercial
        <input type="number" value={filtros.periodo} onChange={(e) => setFiltros({ ...filtros, periodo: e.target.value })} placeholder="2025" />
      </label>
      <button className="btn prim" onClick={onBuscar}>Buscar</button>
      <button className="btn" onClick={() => { setFiltros({ mercado: '', origen: '', periodo: '' }); onBuscar() }}>Limpiar</button>
    </div>
  )
}

function CargaCsv({ onResultado }) {
  const [tipo, setTipo] = useState('montos')
  const [abierto, setAbierto] = useState(false)
  const [archivo, setArchivo] = useState(null)
  const [msg, setMsg] = useState('')
  return (
    <>
      <button className="btn" onClick={() => setAbierto(!abierto)}>Carga de calificaciones</button>
      {abierto && (
        <div className="modal">
          <div className="modal-caja">
            <h2>Cargar archivo (CSV)</h2>
            <label>Tipo de carga
              <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
                <option value="montos">Montos (DJ 1948)</option>
                <option value="factores">Factores (8-37)</option>
              </select>
            </label>
            <label>Archivo
              <input type="file" accept=".csv" onChange={(e) => setArchivo(e.target.files[0])} />
            </label>
            <p className="nota">Columnas: ejercicio, mercado, instrumento, fecha (YYYY-MM-DD), secuencia, numero_dividendo, tipo_sociedad (A/C), valor_historico, monto_8…monto_19 / factor_8…factor_37. Actualiza por llave si existe.</p>
            {msg && <p className="aviso">{msg}</p>}
            <div className="modal-botones">
              <button className="btn" onClick={() => setAbierto(false)}>Cancelar</button>
              <button className="btn prim" onClick={async () => {
                if (!archivo) { setMsg('Selecciona un archivo CSV'); return }
                try {
                  const r = await api.cargar(archivo, tipo)
                  setMsg(`OK: ${r.insertados} insertados, ${r.actualizados} actualizados${r.errores?.length ? ` — errores: ${r.errores.join('; ')}` : ''}`)
                  onResultado(r); setAbierto(false)
                } catch (e) { setMsg(e.message) }
              }}>Grabar</button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

function convertirForm(f) {
  return {
    ejercicio: f.ejercicio, mercado: f.mercado, instrumento: f.instrumento,
    fecha_pago: f.fecha_pago, secuencia: f.secuencia, numero_dividendo: f.numero_dividendo,
    tipo_sociedad: f.tipo_sociedad, valor_historico: f.valor_historico, isfut: !!f.isfut,
    origen: f.origen, montos: f.montos || {}, factores: f.factores || {},
  }
}

function ModalCalificacion({ modal, onClose, onGuardado }) {
  const [form, setForm] = useState(modal.form)
  const [pestana, setPestana] = useState('basicos')
  const [error, setError] = useState('')
  const set = (k, v) => setForm({ ...form, [k]: v })
  const setMonto = (c, v) => setForm({ ...form, montos: { ...form.montos, [c]: v === '' ? 0 : Number(v) } })
  const setFactor = (c, v) => setForm({ ...form, factores: { ...form.factores, [c]: v === '' ? 0 : Number(v) } })

  async function guardar() {
    setError('')
    if (!form.mercado || !form.instrumento || !form.fecha_pago) { setError('Mercado, instrumento y fecha pago son obligatorios'); return }
    const data = {
      ...form,
      secuencia: Number(form.secuencia) || 0,
      numero_dividendo: Number(form.numero_dividendo) || 0,
      valor_historico: Number(form.valor_historico) || 0,
      montos: form.montos, factores: form.factores,
    }
    onGuardado(data)
  }

  return (
    <div className="modal">
      <div className="modal-caja ancha">
        <h2>{modal.modo === 'crear' ? 'Ingresar Calificación' : `Modificar Calificación #${modal.id}`}</h2>
        <div className="pestanas">
          <button className={pestana === 'basicos' ? 'tab act' : 'tab'} onClick={() => setPestana('basicos')}>Datos básicos</button>
          <button className={pestana === 'montos' ? 'tab act' : 'tab'} onClick={() => setPestana('montos')}>Montos (29 campos)</button>
          <button className={pestana === 'factores' ? 'tab act' : 'tab'} onClick={() => setPestana('factores')}>Factores</button>
        </div>

        {pestana === 'basicos' && (
          <div className="form-grid">
            <label>Mercado <select value={form.mercado} onChange={(e) => set('mercado', e.target.value)}><option value="">—</option><option>ACN</option><option>CFI</option><option>FM</option></select></label>
            <label>Instrumento <input value={form.instrumento} onChange={(e) => set('instrumento', e.target.value)} /></label>
            <label>Ejercicio <input type="number" value={form.ejercicio} onChange={(e) => set('ejercicio', Number(e.target.value))} /></label>
            <label>Fecha pago <input type="date" value={formatFecha(form.fecha_pago)} onChange={(e) => set('fecha_pago', e.target.value)} /></label>
            <label>Secuencia evento <input type="number" value={form.secuencia} onChange={(e) => set('secuencia', e.target.value)} /></label>
            <label>N° dividendo <input type="number" value={form.numero_dividendo} onChange={(e) => set('numero_dividendo', e.target.value)} /></label>
            <label>Tipo sociedad
              <select value={form.tipo_sociedad} onChange={(e) => set('tipo_sociedad', e.target.value)}>
                <option value="A">Abierta (A)</option><option value="C">Cerrada (C)</option>
              </select>
            </label>
            <label>Valor histórico <input type="number" step="any" value={form.valor_historico} onChange={(e) => set('valor_historico', e.target.value)} /></label>
            <label>Origen
              <select value={form.origen} onChange={(e) => set('origen', e.target.value)}>
                <option>corredor</option><option>entidad</option>
              </select>
            </label>
            <label className="chk"><input type="checkbox" checked={form.isfut} onChange={(e) => set('isfut', e.target.checked)} /> ISFUT</label>
          </div>
        )}

        {pestana === 'montos' && (
          <div className="scroll-cols">
            {MONTOS_COLS.map((c) => (
              <label key={c} className="col-campo">
                <span>{c}. {LABELS[c]}</span>
                <input type="number" step="any" value={form.montos[c] ?? ''} onChange={(e) => setMonto(c, e.target.value)} />
              </label>
            ))}
          </div>
        )}

        {pestana === 'factores' && (
          <div className="scroll-cols">
            {MONTOS_COLS.map((c) => (
              <label key={c} className="col-campo">
                <span>{c}. {LABELS[c]}</span>
                <input type="number" step="0.00000001" value={form.factores[c] ?? ''} onChange={(e) => setFactor(c, e.target.value)} />
              </label>
            ))}
          </div>
        )}

        {error && <p className="aviso err">{error}</p>}
        <div className="modal-botones">
          <button className="btn" onClick={onClose}>Cancelar</button>
          <button className="btn prim" onClick={guardar}>Guardar</button>
        </div>
      </div>
    </div>
  )
}

function ModalDetalle({ detalle, onClose, onCalcular }) {
  const suma = sumaBase(detalle.factores || {})
  return (
    <div className="modal">
      <div className="modal-caja ancha">
        <h2>{detalle.instrumento} — ej. {detalle.ejercicio} ({detalle.mercado})</h2>
        <p className="sub">Secuencia {detalle.secuencia} · N° div. {detalle.numero_dividendo} · {detalle.tipo_sociedad === 'A' ? 'Abierta' : 'Cerrada'} · ISFUT {detalle.isfut ? 'Sí' : 'No'} · Origen {detalle.origen} · Fuente {detalle.fuente}</p>
        <div className="resumen">
          <strong>Suma factores 8–19: {suma.toFixed(8)}</strong> {suma > 1 ? <span className="peligro-texto"> ¡supera 1!</span> : ' (≤ 1 ✓)'}
        </div>
        <div className="scroll-cols">
          {MONTOS_COLS.map((c) => (
            <div key={c} className="fila-detalle">
              <span className="num">{c}</span>
              <span className="lbl">{LABELS[c]}</span>
              <span className="val">M: {(detalle.montos?.[c] ?? 0).toLocaleString('es-CL')}</span>
              <span className="val">F: {detalle.factores?.[c] ?? '—'}</span>
            </div>
          ))}
        </div>
        <div className="modal-botones">
          <button className="btn" onClick={onClose}>Cerrar</button>
          <button className="btn prim" onClick={onCalcular}>Calcular factores</button>
        </div>
      </div>
    </div>
  )
}

function Auditoria() {
  const [rows, setRows] = useState([])
  useEffect(() => { api.auditoria().then(setRows).catch(() => {}) }, [])
  return (
    <div>
      <h2>Log de auditoría</h2>
      <table className="grilla">
        <thead><tr><th>#</th><th>Fecha</th><th>Acción</th><th>Registro</th><th>Detalle</th><th>Usuario</th></tr></thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}><td>{r.id}</td><td>{r.fecha}</td><td>{r.accion}</td><td>{r.registro_id ?? ''}</td><td>{r.detalle}</td><td>{r.usuario}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
