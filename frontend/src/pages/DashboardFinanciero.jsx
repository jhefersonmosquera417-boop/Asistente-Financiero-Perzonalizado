import { useMemo, useState } from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Legend,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'
import { mapearPortafolioConProductos } from '../services/productMapper'
import './DashboardFinanciero.css'

const COLORS = ['#22C55E', '#3B82F6', '#F59E0B', '#8B5CF6', '#06B6D4', '#F97316']
const tabs = ['Tu Portafolio', 'Proyecciones', 'Recomendaciones']

function DashboardFinanciero({ data, onBack }) {
  const [activeTab, setActiveTab] = useState('Tu Portafolio')
  const [showJson, setShowJson] = useState(false)

  const datosPerfil = useMemo(() => {
    const horizonString = data?.horizonte || '2 años'
    const horizonMatch = horizonString.match(/(\d+)\s*años?/) || []
    const horizonte_anos = Number(horizonMatch[1]) || 2
    return {
      salario: data?.salario || 0,
      riesgo: data?.nivel_riesgo || 'Bajo',
      horizonte: data?.horizonte || 'Corto plazo (2 años)',
      ahorro_inversion: data?.ahorro_inversion || 0,
      horizonte_anos,
      objetivo: data?.objetivo_financiero || 'Fondo de emergencia',
    }
  }, [data])

  const portfolioMapeado = useMemo(
    () => mapearPortafolioConProductos(data?.portafolio_optimo || [], datosPerfil),
    [data?.portafolio_optimo, datosPerfil]
  )

  const barData = useMemo(() => {
    const totalProyectado = data?.valor_proyectado || 0
    const anos = datosPerfil.horizonte_anos || 1
    return Array.from({ length: anos }, (_, i) => ({
      year: `Año ${i + 1}`,
      Proyectado: Math.round((totalProyectado / anos) * (i + 1)),
    }))
  }, [data?.valor_proyectado, datosPerfil.horizonte_anos])

  const pieData = useMemo(
    () =>
      portfolioMapeado.map((item) => ({
        name: item.producto?.nombre || item.categoria || 'Activo',
        value: item.monto_mensual || 0,
      })),
    [portfolioMapeado]
  )

  const analisisDetallado =
    data?.recomendacion || data?.mensaje || 'Generando análisis del portafolio evolutivo...'

  return (
    <div className="dashboard-shell">
      <div style={{ maxWidth: '1100px', margin: '0 auto', width: '100%', padding: '0 1.5rem' }}>

        {/* ── TOPBAR ── */}
        <div className="dashboard-topbar">
          <div>
            <span className="eyebrow">FinAI Colombia</span>
            <h1>Tu Plan Financiero Personalizado</h1>
            <p>Portafolio optimizado con productos reales según tu perfil financiero.</p>
          </div>
          <button className="ghost-button" onClick={onBack}>
            Volver al formulario
          </button>
        </div>

        {/* ── KPI GRID ── */}
        <div className="kpi-grid">
          <div className="kpi-card green">
            <span>Score financiero</span>
            <strong>70 / 100</strong>
            <p>Perfil Saludable</p>
          </div>
          <div className="kpi-card blue">
            <span>Inversión mensual recomendada</span>
            <strong>{(data?.ahorro_inversion || 0).toLocaleString('es-CO')} COP</strong>
            <p>20% de tu salario</p>
          </div>
          <div className="kpi-card yellow">
            <span>Valor Proyectado Total</span>
            <strong>{(data?.valor_proyectado || 0).toLocaleString('es-CO')} COP</strong>
            <p>Estimación del algoritmo</p>
          </div>
          <div className="kpi-card purple">
            <span>Horizonte de inversión</span>
            <strong>{datosPerfil.horizonte_anos} años</strong>
            <p>{datosPerfil.horizonte}</p>
          </div>
        </div>

        {/* ── TABS ── */}
        <div className="dashboard-tabs">
          {tabs.map((tab) => (
            <button
              key={tab}
              className={activeTab === tab ? 'tab-button active' : 'tab-button'}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* ── PANEL ── */}
        <div className="dashboard-panel">

          {/* TAB: Tu Portafolio */}
          {activeTab === 'Tu Portafolio' && (
            <div className="panel-grid">

              {/* Inspector JSON para el profesor */}
              <div
                className="panel-card full-width"
                style={{ border: '1px solid #3b82f6', background: '#0f172a' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
                  <div>
                    <h2 style={{ color: '#3b82f6', margin: 0 }}>
                      Portafolio generado por algoritmo evolutivo
                    </h2>
                    <p style={{ color: '#94a3b8', margin: '4px 0 0', fontSize: '0.9rem' }}>
                      Verifica la trazabilidad del catálogo y los datos JSON del backend.
                    </p>
                  </div>
                  <button
                    className={`btn-inspector ${showJson ? 'code-active' : 'code-inactive'}`}
                    onClick={() => setShowJson(!showJson)}
                  >
                    <span className="btn-icon">{showJson ? '⚡' : '🔍'}</span>
                    {showJson ? 'Ocultar portafolio JSON' : 'Ver portafolio JSON'}
                    <span className="btn-arrow">{showJson ? '▲' : '▼'}</span>
                  </button>
                </div>

                {showJson && (
                  <div style={{ marginTop: '15px', background: '#020617', padding: '15px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <p style={{ color: '#cbd5e1', fontSize: '0.9rem', marginBottom: '10px' }}>
                      <strong>Análisis técnico:</strong> El algoritmo genético procesó el catálogo
                      de inversiones colombianas, aplicando restricciones de riesgo{' '}
                      <strong>{datosPerfil.riesgo}</strong> y asignó pesos óptimos en base a la
                      función de aptitud (fitness):
                    </p>
                    <pre style={{
                      color: '#4ade80',
                      fontFamily: 'monospace',
                      fontSize: '0.85rem',
                      overflowX: 'auto',
                      backgroundColor: '#090d16',
                      padding: '12px',
                      borderRadius: '6px',
                    }}>
                      {JSON.stringify(data?.portafolio_optimo, null, 2)}
                    </pre>
                  </div>
                )}
              </div>

              {/* Tarjeta de perfil del usuario */}
              <div className="panel-card compact" style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
                <h2 style={{ marginBottom: '1rem' }}>Tu perfil financiero</h2>

                {/* Avatar + nombre de perfil */}
                <div style={{
                  display: 'flex', alignItems: 'center', gap: '12px',
                  background: 'rgba(59,130,246,0.07)', borderRadius: '10px',
                  padding: '12px 14px', marginBottom: '1rem',
                }}>
                  <div style={{
                    width: '44px', height: '44px', borderRadius: '50%',
                    background: 'rgba(59,130,246,0.15)', border: '2px solid #3b82f6',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '1.2rem', flexShrink: 0,
                  }}>
                    {datosPerfil.riesgo === 'Alto' ? '🚀' : datosPerfil.riesgo === 'Medio' ? '⚖️' : '🛡️'}
                  </div>
                  <div>
                    <p style={{ margin: 0, color: '#e2e8f0', fontWeight: '600', fontSize: '0.95rem' }}>
                      Perfil {datosPerfil.riesgo}
                    </p>
                    <p style={{ margin: 0, color: '#64748b', fontSize: '0.8rem' }}>
                      {datosPerfil.objetivo}
                    </p>
                  </div>
                </div>

                {/* Filas de datos */}
                {[
                  { label: 'Salario mensual', value: `${(datosPerfil.salario).toLocaleString('es-CO')} COP`, icon: '💰' },
                  { label: 'Nivel de riesgo',  value: datosPerfil.riesgo, icon: '📊' },
                  { label: 'Horizonte',         value: datosPerfil.horizonte, icon: '🗓️' },
                  { label: 'Fondo emergencia',  value: data?.fondo_emergencia ? 'Incluido ✓' : 'No incluido', icon: '🆘' },
                ].map((row, i) => (
                  <div key={i} style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '10px 0',
                    borderBottom: i < 3 ? '1px solid rgba(255,255,255,0.05)' : 'none',
                  }}>
                    <span style={{ color: '#64748b', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span>{row.icon}</span>{row.label}
                    </span>
                    <span style={{ color: '#cbd5e1', fontWeight: '500', fontSize: '0.85rem', textAlign: 'right', maxWidth: '55%' }}>
                      {row.value}
                    </span>
                  </div>
                ))}

                {/* Regla 50/30/20 */}
                <div style={{ marginTop: '1rem' }}>
                  <p style={{ color: '#64748b', fontSize: '0.8rem', marginBottom: '8px', fontWeight: '600', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                    Regla 50/30/20
                  </p>
                  {[
                    { label: 'Necesidades', pct: 50, color: '#22c55e', valor: Math.round(datosPerfil.salario * 0.50) },
                    { label: 'Deseos',      pct: 30, color: '#3b82f6', valor: Math.round(datosPerfil.salario * 0.30) },
                    { label: 'Ahorro',      pct: 20, color: '#8b5cf6', valor: Math.round(datosPerfil.salario * 0.20) },
                  ].map((item, i) => (
                    <div key={i} style={{ marginBottom: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                        <span style={{ color: '#94a3b8', fontSize: '0.8rem' }}>{item.label} ({item.pct}%)</span>
                        <span style={{ color: item.color, fontWeight: '600', fontSize: '0.8rem' }}>
                          {item.valor.toLocaleString('es-CO')} COP
                        </span>
                      </div>
                      <div style={{ background: 'rgba(255,255,255,0.06)', borderRadius: '99px', height: '5px', overflow: 'hidden' }}>
                        <div style={{ width: `${item.pct}%`, height: '100%', background: item.color, borderRadius: '99px' }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Pie chart */}
              <div className="panel-card wide">
                <h2>Distribución por tipo de inversión</h2>
                {pieData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={320}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        dataKey="value"
                        nameKey="name"
                        innerRadius={70}
                        outerRadius={120}
                        paddingAngle={3}
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Legend verticalAlign="bottom" height={36} />
                      <Tooltip
                        formatter={(value) =>
                          new Intl.NumberFormat('es-CO').format(value) + ' COP'
                        }
                      />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <p>No hay datos de portafolio disponibles.</p>
                )}
              </div>

              {/* Productos */}
              <div className="panel-card full-width">
                <h2>Productos recomendados con justificación</h2>
                <div className="products-grid">
                  {portfolioMapeado.map((item, index) => (
                    <div key={index} className="product-card">
                      <div className="product-header">
                        <div className="product-info">
                          <span className="badge">{item.categoria}</span>
                          <h3>{item.producto?.nombre || 'Producto sugerido'}</h3>
                          <p className="product-percentage">
                            {item.porcentaje}% de tu inversión mensual
                          </p>
                        </div>
                        <div className="product-amount">
                          <strong className="amount">
                            {(item.monto_mensual || 0).toLocaleString('es-CO')} COP/mes
                          </strong>
                        </div>
                      </div>
                      <div className="product-details">
                        <div className="detail-row">
                          <span className="label">Rentabilidad aproximada:</span>
                          <span className="value">
                            {item.producto?.rentabilidad_anual
                              ? `${(item.producto.rentabilidad_anual * 100).toFixed(1)}% EA`
                              : 'Variable'}
                          </span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Nivel de riesgo:</span>
                          <span className="value">
                            {item.producto?.riesgo || datosPerfil.riesgo}
                          </span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Liquidez:</span>
                          <span className="value">
                            {item.producto?.liquidez?.split(' - ')[0] || 'Alta'}
                          </span>
                        </div>
                      </div>
                      <div className="product-justification">
                        <p className="justification-title">
                          Por qué el algoritmo eligió esta opción:
                        </p>
                        <p className="justification-text">
                          {item.justificacion ||
                            'Se adapta a tu nivel de riesgo y horizonte temporal.'}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          )}

          {/* TAB: Proyecciones */}
          {activeTab === 'Proyecciones' && (
            <div className="panel-grid">
              <div className="panel-card wide">
                <h2>Proyección de tu inversión en el tiempo</h2>
                {barData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={320}>
                    <BarChart data={barData}>
                      <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                      <XAxis dataKey="year" tick={{ fill: '#94a3b8' }} />
                      <YAxis tick={{ fill: '#94a3b8' }} />
                      <Tooltip
                        formatter={(value) =>
                          new Intl.NumberFormat('es-CO').format(value) + ' COP'
                        }
                      />
                      <Bar dataKey="Proyectado" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <p style={{ color: '#94a3b8' }}>No hay datos de proyección mapeados.</p>
                )}
              </div>
              <div className="panel-card compact">
                <h2>Crecimiento esperado</h2>
                {barData.length > 0 ? (
                  barData.map((item, idx) => (
                    <div key={idx} className="projection-row">
                      <span>{item.year}</span>
                      <strong>{item.Proyectado.toLocaleString('es-CO')} COP</strong>
                    </div>
                  ))
                ) : (
                  <p style={{ color: '#94a3b8' }}>Sin proyecciones acumuladas.</p>
                )}
              </div>
            </div>
          )}

          {/* TAB: Recomendaciones */}
          {activeTab === 'Recomendaciones' && (
            <div className="panel-grid single">
              <div className="panel-card wide">
                <h2>Análisis detallado de tu perfil financiero</h2>
                <div className="analysis-container">
                  {analisisDetallado.split('\n').map((line, idx) => {
                    const trimmed = line.trim()

                    // Línea vacía → separador
                    if (!trimmed) return <div key={idx} style={{ height: '0.5rem' }} />

                    // ── Advertencia crítica salario bajo 🚨
                    if (trimmed.startsWith('🚨')) {
                      const texto = trimmed.replace(/^🚨\s*(SALARIO_BAJO:\s*)?/, '')
                      return (
                        <div key={idx} style={{
                          display: 'flex', alignItems: 'flex-start', gap: '10px',
                          background: 'rgba(239,68,68,0.08)',
                          border: '1px solid rgba(239,68,68,0.35)',
                          borderRadius: '10px', padding: '12px 16px', marginBottom: '1rem',
                        }}>
                          <span style={{ fontSize: '1.1rem', flexShrink: 0 }}>🚨</span>
                          <p style={{ color: '#fca5a5', fontWeight: '500', lineHeight: '1.6', margin: 0 }}>
                            <strong style={{ color: '#f87171' }}>Atención: </strong>{texto}
                          </p>
                        </div>
                      )
                    }

                    // ── Advertencia deuda ⚠️ DEUDA
                    if (trimmed.startsWith('⚠️ DEUDA')) {
                      const texto = trimmed.replace(/^⚠️\s*DEUDA:\s*/, '')
                      return (
                        <div key={idx} style={{
                          display: 'flex', alignItems: 'flex-start', gap: '10px',
                          background: 'rgba(245,158,11,0.08)',
                          border: '1px solid rgba(245,158,11,0.35)',
                          borderRadius: '10px', padding: '12px 16px', marginBottom: '1rem',
                        }}>
                          <span style={{ fontSize: '1.1rem', flexShrink: 0 }}>⚠️</span>
                          <p style={{ color: '#fcd34d', fontWeight: '500', lineHeight: '1.6', margin: 0 }}>
                            <strong style={{ color: '#fbbf24' }}>Deuda activa: </strong>{texto}
                          </p>
                        </div>
                      )
                    }

                    // ── Alerta ⚠️ genérica o ✓
                    if (trimmed.startsWith('⚠️') || trimmed.startsWith('✓')) {
                      return (
                        <div key={idx} style={{
                          background: 'rgba(245,158,11,0.08)',
                          border: '1px solid rgba(245,158,11,0.3)',
                          borderRadius: '8px', padding: '10px 16px', marginBottom: '1rem',
                        }}>
                          <p style={{ color: '#fbbf24', fontWeight: '500', lineHeight: '1.6', margin: 0 }}>
                            {trimmed}
                          </p>
                        </div>
                      )
                    }

                    // ── Encabezado ### con color según emoji
                    if (trimmed.startsWith('### ')) {
                      const titulo = trimmed.replace(/^###\s*/, '')
                      const colorMap = {
                        '👥': { border: '#8b5cf6', bg: 'rgba(139,92,246,0.08)', text: '#c4b5fd' },
                        '📊': { border: '#3b82f6', bg: 'rgba(59,130,246,0.08)', text: '#93c5fd' },
                        '🛡': { border: '#22c55e', bg: 'rgba(34,197,94,0.08)',  text: '#86efac' },
                        '🎯': { border: '#f59e0b', bg: 'rgba(245,158,11,0.08)', text: '#fcd34d' },
                      }
                      const match = Object.keys(colorMap).find(k => titulo.includes(k))
                      const colors = colorMap[match] || { border: '#64748b', bg: 'rgba(100,116,139,0.08)', text: '#94a3b8' }
                      return (
                        <div key={idx} style={{
                          borderLeft: `4px solid ${colors.border}`,
                          background: colors.bg,
                          borderRadius: '0 8px 8px 0',
                          padding: '12px 16px',
                          marginBottom: '1rem',
                          marginTop: idx > 0 ? '1.75rem' : '0',
                        }}>
                          <p style={{ color: colors.text, fontWeight: '600', fontSize: '1rem', margin: 0, lineHeight: '1.4' }}>
                            {titulo}
                          </p>
                        </div>
                      )
                    }

                    // ── Bullet con valor: * Clave: valor
                    if (trimmed.startsWith('* ') || trimmed.startsWith('• ') || trimmed.startsWith('- ')) {
                      const text = trimmed.replace(/^(\*|•|-)\s+/, '')
                      const partes = text.split(/:(.+)/)
                      const tieneValor = partes.length >= 2

                      // Formatear números grandes sin comas → con puntos colombianos
                      const formatearValor = (v) => {
                        const limpio = v.trim().replace(/\$|COP|%|\(|\)/g, '').trim()
                        const num = parseInt(limpio.replace(/,/g, ''), 10)
                        if (!isNaN(num) && num > 999) {
                          return v.trim().replace(limpio, num.toLocaleString('es-CO'))
                        }
                        return v.trim()
                      }

                      return (
                        <div key={idx} style={{
                          display: 'flex', alignItems: 'flex-start', gap: '10px',
                          padding: '10px 14px', marginBottom: '6px',
                          background: 'rgba(59,130,246,0.05)',
                          borderLeft: '3px solid #3b82f6',
                          borderRadius: '0 8px 8px 0',
                        }}>
                          <span style={{ color: '#3b82f6', fontWeight: '700', flexShrink: 0, marginTop: '2px' }}>›</span>
                          <p style={{ color: '#cbd5e1', lineHeight: '1.6', margin: 0, flex: 1 }}>
                            {tieneValor ? (
                              <>
                                <strong style={{ color: '#e2e8f0' }}>{partes[0]}:</strong>
                                <span style={{ color: '#22c55e', fontWeight: '600' }}>{formatearValor(partes[1])}</span>
                              </>
                            ) : text}
                          </p>
                        </div>
                      )
                    }

                    // ── Párrafo normal
                    return (
                      <p key={idx} style={{
                        color: '#94a3b8', lineHeight: '1.8',
                        marginBottom: '0.75rem', fontSize: '0.95rem',
                      }}>
                        {trimmed}
                      </p>
                    )
                  })}
                </div>
              </div>
            </div>
          )}

        </div>{/* /dashboard-panel */}

        {/* ── DISCLAIMER ── */}
        <div style={{
          marginTop: '60px',
          marginBottom: '40px',
          padding: '32px 40px',
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid #334155',
          borderRadius: '16px',
          textAlign: 'center',
        }}>
          <p style={{
            fontSize: '0.7rem',
            fontWeight: '600',
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: '#64748b',
            marginBottom: '12px',
          }}>
            ⚠️ Aviso Legal — Disclaimer
          </p>
          <p style={{
            color: '#94a3b8',
            fontSize: '0.92rem',
            lineHeight: '1.8',
            maxWidth: '780px',
            margin: '0 auto',
          }}>
            <strong style={{ color: '#cbd5e1' }}>FinAI Colombia</strong> es una plataforma de
            simulación con fines <strong style={{ color: '#cbd5e1' }}>puramente académicos</strong>.
            Este portafolio es generado mediante algoritmos genéticos y{' '}
            <strong style={{ color: '#cbd5e1' }}>no constituye asesoría financiera</strong> legal,
            profesional ni vinculante. Las tasas de rentabilidad, proyecciones de inversión y
            selección de productos son meramente ilustrativas y no garantizan rendimientos futuros.
            Antes de realizar cualquier inversión real, consulte con una entidad financiera
            vigilada por la{' '}
            <strong style={{ color: '#cbd5e1' }}>Superintendencia Financiera de Colombia</strong>.
          </p>
        </div>

      </div>{/* /max-width wrapper */}
    </div>
  )
}

export default DashboardFinanciero