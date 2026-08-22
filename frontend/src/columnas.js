// Etiquetas de las columnas 8-37 segun hoja 3.TIpos de datos / 3.2 Homologacion
export const LABELS = {
  8: 'Con crédito IDPC (gen. 01.01.2017)',
  9: 'Con crédito IDPC (acum. 31.12.2016)',
  10: 'Con derecho crédito pago IDPC voluntario',
  11: 'Sin derecho a crédito',
  12: 'RAP y Dif. Inicial (ex Art. 14 TER A)',
  13: 'Otras rentas percibidas sin prioridad',
  14: 'Exceso Distribuciones Desproporcionadas (N°9 Art.14 A)',
  15: 'ISFUT Ley N°20.780',
  16: 'Rentas hasta 31.12.1983 / ISFUT Ley N°21.210',
  17: 'Rentas exentas IGC (Art.11 L.18.401) afectas a IA',
  18: 'Rentas exentas IGC y/o IA',
  19: 'Ingresos No Constitutivos de Renta',
  20: 'No sujetos restitución hasta 31.12.2019 sin derecho',
  21: 'No sujetos restitución hasta 31.12.2019 con derecho',
  22: 'No sujetos restitución desde 01.01.2020 sin derecho',
  23: 'No sujetos restitución desde 01.01.2020 con derecho',
  24: 'Sujetos a restitución sin derecho',
  25: 'Sujetos a restitución con derecho',
  26: 'Sujetos a restitución sin derecho (2)',
  27: 'Sujetos a restitución con derecho (2)',
  28: 'Crédito por IPE',
  29: 'Asociados a Rentas Afectas, sin derecho',
  30: 'Asociados a Rentas Afectas, con derecho',
  31: 'Asociados a Rentas Exentas (Art.11 L.18.401), sin derecho',
  32: 'Asociados a Rentas Exentas (Art.11 L.18.401), con derecho',
  33: 'Crédito por IPE (acumulados 31.12.2016)',
  34: 'Crédito impuesto tasa adicional ex Art.21 LIR, sin derecho',
  35: 'Crédito impuesto tasa adicional ex Art.21 LIR, con derecho',
  36: 'Tasa efectiva crédito FUT (TEF)',
  37: 'Tasa efectiva crédito FUT (TEX)',
}

export const MONTOS_COLS = Object.keys(LABELS).map(Number)
export const BASE_COLS = MONTOS_COLS.filter((c) => c <= 19) // base del calculo 8..19

export function formatFecha(iso) {
  if (!iso) return ''
  return iso.slice(0, 10)
}

export function sumaBase(factores) {
  return BASE_COLS.reduce((acc, c) => acc + (factores[c] || 0), 0)
}
