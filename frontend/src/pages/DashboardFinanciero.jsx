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
import { mapearPortafolioConProductos, generarAnalisisPersonalizado } from '../services/productMapper'
import './DashboardFinanciero.css'

const COLORS = ['#22C55E', '#3B82F6', '#F59E0B', '#8B5CF6', '#06B6D4', '#F97316']
const tabs = ['Tu Portafolio', 'Proyecciones', 'Recomendaciones']

function DashboardFinanciero({ data, onBack }) {
  const [activeTab, setActiveTab] = useState('Tu Portafolio')

  // Mapear portafolio a productos reales con justificaciones
  const datosPerfil = useMemo(() => {
    const perfil = data.perfil || {}
    const horizonString = perfil.horizonte || data.horizonte || ''
    const horizonMatch = horizonString.match(/(\d+)\s*años?/) || []
    const horizonte_anos = Number(horizonMatch[1]) ||
      (horizonString.includes('Corto') ? 2 :
      horizonString.includes('Largo') ? 10 : 5)

    return {
      salario: perfil.salario || 0,
      gastos_fijos: perfil.gastos_fijos || 0,
      deudas: perfil.deudas || 0,
      riesgo: perfil.riesgo || 'Medio',
      horizonte: perfil.horizonte || 'Mediano plazo',
      ahorro_inversion: data.distribucion_mensual?.ahorro_inversion || 0,
      horizonte_anos,
      objetivo: Array.isArray(perfil.objetivos) ? perfil.objetivos[0] : perfil.objetivos || 'Inversión general',
    }
  }, [data])

  const portfolioMapeado = useMemo(
    () => mapearPortafolioConProductos(data.portafolio_optimo || [], datosPerfil),
    [data.portafolio_optimo, datosPerfil]
  )

  const analisisPersonalizado = useMemo(
    () => generarAnalisisPersonalizado(datosPerfil, data),
    [datosPerfil, data]
  )

  const pieData = useMemo(
    () =>
      portfolioMapeado.map((item) => ({
        name: item.producto?.nombre || item.categoria,
        value: item.monto_mensual || 0,
      })),
    [portfolioMapeado]
  )

  const barData = useMemo(
    () =>
      Object.entries(data.proyecciones || {}).map(([year, value]) => ({
        year: `${year} años`,
        'Proyectado': value.valor_proyectado,
      })),
    [data.proyecciones]
  )

  return (
    <div className="dashboard-shell">
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

      <div className="kpi-grid">
        <div className="kpi-card green">
          <span>Score financiero</span>
          <strong>{data.score_financiero}</strong>
          <p>{data.score_label}</p>
        </div>
        <div className="kpi-card blue">
          <span>Inversión mensual recomendada</span>
          <strong>{data.distribucion_mensual.ahorro_inversion.toLocaleString('es-CO')} COP</strong>
          <p>20% de tu salario</p>
        </div>
        <div className="kpi-card yellow">
          <span>Rentabilidad esperada anual</span>
          <strong>{Math.round((data.distribucion_mensual.ahorro_inversion * 12) * 0.08).toLocaleString('es-CO')} COP</strong>
          <p>Proyección conservadora</p>
        </div>
        <div className="kpi-card purple">
          <span>Horizonte de inversión</span>
          <strong>{datosPerfil.horizonte_anos} años</strong>
          <p>{data.horizonte || 'Mediano plazo'}</p>
        </div>
      </div>

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

      <div className="dashboard-panel">
        {activeTab === 'Tu Portafolio' && (
          <div className="panel-grid">
            <div className="panel-card wide">
              <h2>Distribución por Tipo de Inversión</h2>
              <ResponsiveContainer width="100%" height={320}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={70} outerRadius={120} paddingAngle={3}>
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Legend verticalAlign="bottom" height={36} />
                  <Tooltip formatter={(value) => new Intl.NumberFormat('es-CO').format(value)} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="panel-card full-width">
              <h2>Productos Recomendados con Justificación</h2>
              <div className="products-grid">
                {portfolioMapeado.map((item, index) => (
                  <div key={index} className="product-card">
                    <div className="product-header">
                      <div className="product-info">
                        <span className="badge">{item.categoria}</span>
                        <h3>{item.producto?.nombre || 'No disponible'}</h3>
                        <p className="product-percentage">{item.porcentaje}% de tu inversión mensual</p>
                      </div>
                      <div className="product-amount">
                        <strong className="amount">{(item.monto_mensual || 0).toLocaleString('es-CO')} COP/mes</strong>
                      </div>
                    </div>

                    {item.producto && (
                      <>
                        <div className="product-details">
                          <div className="detail-row">
                            <span className="label">Rentabilidad anual:</span>
                            <span className="value">{(item.producto.rentabilidad_anual * 100).toFixed(1)}%</span>
                          </div>
                          <div className="detail-row">
                            <span className="label">Nivel de riesgo:</span>
                            <span className="value">{item.producto.riesgo}</span>
                          </div>
                          <div className="detail-row">
                            <span className="label">Liquidez:</span>
                            <span className="value">{item.producto.liquidez.split(' - ')[0]}</span>
                          </div>
                          <div className="detail-row">
                            <span className="label">Monto mínimo:</span>
                            <span className="value">{item.producto.monto_minimo.toLocaleString('es-CO')} COP</span>
                          </div>
                        </div>

                        <div className="product-justification">
                          <p className="justification-title">Por qué se eligió este producto:</p>
                          <p className="justification-text">{item.justificacion}</p>
                        </div>

                        <div className="product-features">
                          <p className="features-title">Características:</p>
                          <ul>
                            {item.producto.caracteristicas.map((feature, idx) => (
                              <li key={idx}>{feature}</li>
                            ))}
                          </ul>
                        </div>
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'Proyecciones' && (
          <div className="panel-grid">
            <div className="panel-card wide">
              <h2>Proyección de tu Inversión</h2>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={barData}>
                  <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                  <XAxis dataKey="year" tick={{ fill: '#94a3b8' }} />
                  <YAxis tick={{ fill: '#94a3b8' }} />
                  <Tooltip formatter={(value) => new Intl.NumberFormat('es-CO').format(value)} />
                  <Bar dataKey="Proyectado" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="panel-card compact">
              <h2>Crecimiento Esperado</h2>
              {Object.entries(data.proyecciones || {}).map(([year, item]) => (
                <div key={year} className="projection-row">
                  <span>{year} año{year !== '1' ? 's' : ''}</span>
                  <strong>{item.valor_proyectado.toLocaleString('es-CO')} COP</strong>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'Recomendaciones' && (
          <div className="panel-grid single">
            <div className="panel-card wide">
              <h2>Análisis Detallado de tu Perfil Financiero</h2>
              <div className="analysis-container">
                {analisisPersonalizado.split('\n').map((line, idx) => {
                  // Detectar encabezados y formatear apropiadamente
                  if (line.startsWith('**') && line.endsWith('**')) {
                    return (
                      <h3 key={idx} style={{ marginTop: '1.5rem', marginBottom: '0.8rem', color: '#06b6d4', fontWeight: '600' }}>
                        {line.replace(/\*\*/g, '')}
                      </h3>
                    )
                  }
                  if (line.startsWith('•')) {
                    return (
                      <p key={idx} style={{ marginLeft: '1.5rem', marginBottom: '0.5rem', color: '#cbd5e1', lineHeight: '1.6' }}>
                        {line}
                      </p>
                    )
                  }
                  if (line.startsWith('⚠️') || line.startsWith('✓') || line.startsWith('🎯')) {
                    return (
                      <p key={idx} style={{ marginBottom: '0.8rem', color: line.startsWith('⚠️') ? '#ef4444' : '#22c55e', fontWeight: '500', lineHeight: '1.6' }}>
                        {line}
                      </p>
                    )
                  }
                  if (line.trim() === '') {
                    return <div key={idx} style={{ height: '0.5rem' }} />
                  }
                  return (
                    <p key={idx} style={{ marginBottom: '0.5rem', color: '#cbd5e1', lineHeight: '1.6' }}>
                      {line}
                    </p>
                  )
                })}
              </div>
            </div>

            {data.recomendaciones && data.recomendaciones.length > 0 && (
              <div className="panel-card compact">
                <h2>Acciones Recomendadas</h2>
                <div className="recommendation-list">
                  {data.recomendaciones.map((item, index) => (
                    <div key={index} className="recommendation-item">
                      <p>{item}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default DashboardFinanciero
