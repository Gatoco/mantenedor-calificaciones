const API = '/api'

async function request(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Error ${res.status}`)
  }
  if (res.status === 204) return null
  return res.json()
}

export const api = {
  listar: (filtros) => {
    const q = new URLSearchParams()
    if (filtros.mercado) q.set('mercado', filtros.mercado)
    if (filtros.origen) q.set('origen', filtros.origen)
    if (filtros.periodo) q.set('periodo', filtros.periodo)
    const s = q.toString()
    return request('/calificaciones' + (s ? `?${s}` : ''))
  },
  obtener: (id) => request(`/calificaciones/${id}`),
  crear: (data) => request('/calificaciones', { method: 'POST', body: JSON.stringify(data) }),
  modificar: (id, data) => request(`/calificaciones/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  eliminar: (id) => request(`/calificaciones/${id}`, { method: 'DELETE' }),
  calcular: (id) => request(`/calificaciones/${id}/calcular`, { method: 'POST' }),
  auditoria: () => request('/auditoria'),
  cargar: async (archivo, tipo) => {
    const fd = new FormData()
    fd.append('archivo', archivo)
    const res = await fetch(`${API}/carga?tipo=${tipo}`, { method: 'POST', body: fd })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.detail || `Error ${res.status}`)
    }
    return res.json()
  },
}
