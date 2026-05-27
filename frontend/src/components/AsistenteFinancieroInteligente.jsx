import { useMemo, useState } from 'react'
import { optimizarPortafolioEvolutivo } from '../api/finanzas'
import './AsistenteFinancieroInteligente.css'

const SMMLV = 1750905

const pasos = ['Ingresos', 'Perfil de riesgo', 'Objetivos', 'Confirmación']
const objetivosOpciones = [
  'Fondo de emergencia',
  'Comprar vivienda',
  'Educación',
  'Jubilación',
  'Viaje / ocio',
  'Emprendimiento',
]

function AsistenteFinancieroInteligente({ onBack, onComplete }) {
  const [stage, setStage] = useState('landing')
  const [step, setStep] = useState(0)
  const [salario, setSalario] = useState('')
  const [gastosFijos, setGastosFijos] = useState('')
  const [deudas, setDeudas] = useState('')
  const [riesgo, setRiesgo] = useState('Medio')
  const [horizonte, setHorizonte] = useState(5)
  const [objetivos, setObjetivos] = useState(['Fondo de emergencia'])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const salarioNum   = Number(salario   || 0)
  const gastosNum    = Number(gastosFijos || 0)
  const deudasNum    = Number(deudas    || 0)

  // ── Advertencias en tiempo real ──────────────────────────────
  const esBajoSmmlv     = salarioNum > 0 && salarioNum < SMMLV
  const tieneDeuda      = deudasNum > 0
  const ratioDeuda      = salarioNum > 0 ? (deudasNum / salarioNum) * 100 : 0
  const deudaAlta       = ratioDeuda > 30   // más del 30% del salario en deudas = alerta

  const distribucion = useMemo(() => ({
    necesidades:      Math.round(salarioNum * 0.5),
    deseos:           Math.round(salarioNum * 0.3),
    ahorro_inversion: Math.round(salarioNum * 0.2),
  }), [salarioNum])

  // Ahorro real disponible descontando deudas
  const ahorroReal = useMemo(() => {
    const bruto = distribucion.ahorro_inversion
    const libre = bruto - deudasNum
    return libre > 0 ? libre : 0
  }, [distribucion.ahorro_inversion, deudasNum])

  const horizonteLabel = useMemo(() => {
    if (horizonte <= 2) return 'Corto plazo'
    if (horizonte <= 5) return 'Mediano plazo'
    return 'Largo plazo'
  }, [horizonte])

  const handleToggleObjetivo = (objetivo) => {
    setObjetivos((prev) =>
      prev.includes(objetivo)
        ? prev.filter((item) => item !== objetivo)
        : [...prev, objetivo]
    )
  }

  const validarPaso = () => {
    if (step === 0) {
      if (!salarioNum || salarioNum <= 0) return 'Ingresa un salario válido.'
      if (gastosNum < 0) return 'Gastos fijos no pueden ser negativos.'
      if (deudasNum < 0) return 'Deudas no pueden ser negativas.'
    }
    if (step === 1 && !riesgo) return 'Selecciona tu perfil de riesgo.'
    if (step === 2 && objetivos.length === 0) return 'Selecciona al menos un objetivo financiero.'
    return ''
  }

  const avanzarPaso = () => {
    const validation = validarPaso()
    if (validation) { setError(validation); return }
    setError('')
    setStep((prev) => Math.min(prev + 1, pasos.length - 1))
  }

  const retrocederPaso = () => {
    if (step === 0) { onBack(); return }
    setError('')
    setStep((prev) => Math.max(prev - 1, 0))
  }

  const enviarAnalisis = async () => {
    setError('')
    setLoading(true)
    try {
      const payload = {
        salario:              salarioNum,
        nivel_riesgo:         riesgo,
        objetivo_financiero:  objetivos.join(', '),
        horizonte:            horizonteLabel,
        fondo_emergencia:     objetivos.includes('Fondo de emergencia'),
        // ── campos de endeudamiento ──
        deudas_monto:         deudasNum,                   // monto total de deudas
        tiene_endeudamiento:  tieneDeuda,                  // boolean para el backend
        gastos_fijos:         gastosNum,                   // gastos fijos mensuales
        ahorro_real:          ahorroReal,                  // ahorro disponible real
      }
      const response = await optimizarPortafolioEvolutivo(payload)

      // Mezclar respuesta del backend con valores del formulario
      // El backend a veces devuelve nivel_riesgo/fondo_emergencia incorrectos
      // Los valores del formulario son la fuente de verdad
      const responseConPerfil = {
        ...response,
        nivel_riesgo:        riesgo,                                    // siempre del formulario
        fondo_emergencia:    objetivos.includes('Fondo de emergencia'), // siempre del formulario
        horizonte:           `${horizonteLabel} (${horizonte} años)`,   // con años incluidos
        objetivo_financiero: objetivos.join(', '),                      // siempre del formulario
        salario:             salarioNum,                                // siempre del formulario
      }
      onComplete(responseConPerfil)
    } catch (err) {
      setError(err.message || 'Error conectando con el motor genético Python.')
    } finally {
      setLoading(false)
    }
  }

  // ── Bloque de advertencias reutilizable ──────────────────────
  const renderAdvertencias = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' }}>
      {esBajoSmmlv && (
        <div style={{
          display: 'flex', alignItems: 'flex-start', gap: '10px',
          background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.3)',
          borderRadius: '10px', padding: '12px 14px',
        }}>
          <span style={{ fontSize: '1.1rem', flexShrink: 0 }}>🚨</span>
          <div>
            <p style={{ margin: '0 0 2px', color: '#f87171', fontWeight: '600', fontSize: '0.9rem' }}>
              Salario por debajo del mínimo vigente ({SMMLV.toLocaleString('es-CO')} COP)
            </p>
            <p style={{ margin: 0, color: '#fca5a5', fontSize: '0.85rem', lineHeight: '1.5' }}>
              Con este ingreso es clave blindar primero tu fondo de emergencia antes de invertir,
              para evitar depender de deudas informales en imprevistos.
            </p>
          </div>
        </div>
      )}

      {tieneDeuda && (
        <div style={{
          display: 'flex', alignItems: 'flex-start', gap: '10px',
          background: deudaAlta ? 'rgba(239,68,68,0.06)' : 'rgba(245,158,11,0.07)',
          border: `1px solid ${deudaAlta ? 'rgba(239,68,68,0.3)' : 'rgba(245,158,11,0.3)'}`,
          borderRadius: '10px', padding: '12px 14px',
        }}>
          <span style={{ fontSize: '1.1rem', flexShrink: 0 }}>{deudaAlta ? '🔴' : '⚠️'}</span>
          <div>
            <p style={{ margin: '0 0 2px', color: deudaAlta ? '#f87171' : '#fbbf24', fontWeight: '600', fontSize: '0.9rem' }}>
              Endeudamiento {deudaAlta ? 'alto' : 'moderado'}: {ratioDeuda.toFixed(1)}% de tu salario
            </p>
            <p style={{ margin: '0 0 4px', color: deudaAlta ? '#fca5a5' : '#fcd34d', fontSize: '0.85rem', lineHeight: '1.5' }}>
              {deudaAlta
                ? 'Tus deudas consumen más del 30% del salario. Es recomendable priorizar su pago antes de invertir.'
                : 'Tus deudas están dentro de un rango manejable, pero considera liquidarlas para liberar más ahorro.'}
            </p>
            {ahorroReal > 0 ? (
              <p style={{ margin: 0, color: '#86efac', fontSize: '0.85rem', fontWeight: '500' }}>
                💡 Ahorro real disponible para invertir:{' '}
                <strong>{ahorroReal.toLocaleString('es-CO')} COP/mes</strong>
              </p>
            ) : (
              <p style={{ margin: 0, color: '#f87171', fontSize: '0.85rem', fontWeight: '500' }}>
                ⚡ Con las deudas actuales no queda margen de ahorro disponible.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )

  const renderStepContent = () => {
    switch (step) {
      case 0:
        return (
          <div className="wizard-step-grid">
            <div className="field-group">
              <label>Salario mensual (COP)</label>
              <input
                type="number"
                value={salario}
                onChange={(e) => setSalario(e.target.value)}
                placeholder="Ej. 3500000"
              />
            </div>
            <div className="field-group">
              <label>Gastos fijos mensuales (COP)</label>
              <input
                type="number"
                value={gastosFijos}
                onChange={(e) => setGastosFijos(e.target.value)}
                placeholder="Ej. 1200000"
              />
            </div>
            <div className="field-group">
              <label>Total deudas mensuales (COP)</label>
              <input
                type="number"
                value={deudas}
                onChange={(e) => setDeudas(e.target.value)}
                placeholder="Ej. 450000"
              />
            </div>

            {/* Advertencias en tiempo real */}
            {(esBajoSmmlv || tieneDeuda) && renderAdvertencias()}

            <div className="preview-card">
              <span className="preview-title">Vista previa 50/30/20</span>
              <div className="preview-row">
                <strong>Necesidades</strong>
                <span>{distribucion.necesidades.toLocaleString('es-CO')} COP</span>
              </div>
              <div className="preview-row">
                <strong>Deseos</strong>
                <span>{distribucion.deseos.toLocaleString('es-CO')} COP</span>
              </div>
              <div className="preview-row">
                <strong>Ahorro bruto</strong>
                <span>{distribucion.ahorro_inversion.toLocaleString('es-CO')} COP</span>
              </div>
              {tieneDeuda && (
                <div className="preview-row" style={{ borderTop: '1px solid rgba(255,255,255,0.07)', paddingTop: '8px', marginTop: '4px' }}>
                  <strong style={{ color: '#f87171' }}>Deudas</strong>
                  <span style={{ color: '#f87171' }}>− {deudasNum.toLocaleString('es-CO')} COP</span>
                </div>
              )}
              {tieneDeuda && (
                <div className="preview-row">
                  <strong style={{ color: '#22c55e' }}>Ahorro real</strong>
                  <span style={{ color: '#22c55e', fontWeight: '600' }}>{ahorroReal.toLocaleString('es-CO')} COP</span>
                </div>
              )}
            </div>
          </div>
        )

      case 1:
        return (
          <div className="wizard-step-grid">
            <div className="field-group full-width">
              <label>Perfil de riesgo</label>
              <div className="risk-grid">
                {['Bajo', 'Medio', 'Alto'].map((option) => (
                  <button
                    key={option}
                    type="button"
                    className={`risk-chip ${riesgo === option ? 'active' : ''}`}
                    onClick={() => setRiesgo(option)}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
            <div className="field-group full-width">
              <label>Horizonte de inversión: {horizonteLabel}</label>
              <div className="slider-row">
                <input
                  type="range" min="1" max="10" value={horizonte}
                  onChange={(e) => setHorizonte(Number(e.target.value))}
                />
                <span>{horizonte} años</span>
              </div>
            </div>
          </div>
        )

      case 2:
        return (
          <div className="wizard-step-grid">
            <div className="field-group full-width">
              <label>Objetivos financieros</label>
              <div className="objectives-grid">
                {objetivosOpciones.map((item) => (
                  <button
                    key={item}
                    type="button"
                    className={`objective-chip ${objetivos.includes(item) ? 'selected' : ''}`}
                    onClick={() => handleToggleObjetivo(item)}
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )

      default:
        return (
          <div className="wizard-summary-card">
            <h3>Resumen de tu perfil</h3>
            <div className="summary-row">
              <span>Salario mensual</span>
              <strong>{salarioNum.toLocaleString('es-CO')} COP</strong>
            </div>
            <div className="summary-row">
              <span>Gastos fijos</span>
              <strong>{gastosNum.toLocaleString('es-CO')} COP</strong>
            </div>
            <div className="summary-row">
              <span>Deudas mensuales</span>
              <strong style={{ color: deudasNum > 0 ? '#f87171' : '#94a3b8' }}>
                {deudasNum.toLocaleString('es-CO')} COP
                {deudaAlta && <span style={{ marginLeft: '6px', fontSize: '0.8rem' }}>🔴 Alto</span>}
              </strong>
            </div>
            <div className="summary-row">
              <span>Ahorro real disponible</span>
              <strong style={{ color: '#22c55e' }}>{ahorroReal.toLocaleString('es-CO')} COP</strong>
            </div>
            <div className="summary-row">
              <span>Perfil de riesgo</span>
              <strong>{riesgo}</strong>
            </div>
            <div className="summary-row">
              <span>Horizonte</span>
              <strong>{horizonteLabel} ({horizonte} años)</strong>
            </div>
            <div className="summary-row">
              <span>Objetivos</span>
              <strong>{objetivos.join(' · ')}</strong>
            </div>

            {/* Advertencias en resumen final */}
            {(esBajoSmmlv || tieneDeuda) && renderAdvertencias()}

            <div className="preview-card compact" style={{ marginTop: '16px' }}>
              <span className="preview-title">Distribución mensual</span>
              <div className="preview-row">
                <strong>Necesidades (50%)</strong>
                <span>{distribucion.necesidades.toLocaleString('es-CO')} COP</span>
              </div>
              <div className="preview-row">
                <strong>Deseos (30%)</strong>
                <span>{distribucion.deseos.toLocaleString('es-CO')} COP</span>
              </div>
              <div className="preview-row">
                <strong>Ahorro bruto (20%)</strong>
                <span>{distribucion.ahorro_inversion.toLocaleString('es-CO')} COP</span>
              </div>
              {tieneDeuda && (
                <>
                  <div className="preview-row" style={{ color: '#f87171' }}>
                    <strong style={{ color: '#f87171' }}>− Deudas</strong>
                    <span>− {deudasNum.toLocaleString('es-CO')} COP</span>
                  </div>
                  <div className="preview-row" style={{ borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '8px', marginTop: '4px' }}>
                    <strong style={{ color: '#22c55e' }}>Ahorro real</strong>
                    <span style={{ color: '#22c55e', fontWeight: '700' }}>{ahorroReal.toLocaleString('es-CO')} COP</span>
                  </div>
                </>
              )}
            </div>
          </div>
        )
    }
  }

  const renderFooter = () => {
    if (stage === 'landing') {
      return (
        <button className="primary-button" onClick={() => setStage('form')}>
          Iniciar asistente
        </button>
      )
    }
    return (
      <div className="wizard-actions">
        <button className="secondary-button" onClick={retrocederPaso}>
          {step === 0 ? 'Volver' : 'Anterior'}
        </button>
        {step === pasos.length - 1 ? (
          <button className="primary-button" onClick={enviarAnalisis} disabled={loading}>
            {loading ? 'Calculando Portafolio de Inversión...' : 'Ejecutar análisis'}
          </button>
        ) : (
          <button className="primary-button" onClick={avanzarPaso}>
            Siguiente
          </button>
        )}
      </div>
    )
  }

  return (
    <div className="assistant-shell">
      <div className="assistant-panel">
        <header className="assistant-header">
          <div>
            <span className="eyebrow">FinAI Colombia</span>
            <h1>Asistente Financiero Inteligente</h1>
            <p>Completa los pasos para obtener una propuesta de portafolio optimizado y proyecciones financieras.</p>
          </div>
        </header>

        {stage === 'landing' ? (
          <div className="assistant-landing">
            <div>
              <h2>Panel inteligente con algoritmo genético</h2>
              <p>Un flujo guiado con onboarding financiero, score, recomendaciones y dashboard avanzado.</p>
            </div>
            <button className="primary-button" onClick={() => setStage('form')}>
              Comenzar ahora
            </button>
          </div>
        ) : (
          <>
            <div className="wizard-progress">
              {pasos.map((label, index) => (
                <div key={label} className={`step-pill ${index <= step ? 'active' : ''}`}>
                  <span>{index + 1}</span>
                  <p>{label}</p>
                </div>
              ))}
            </div>
            <div className="wizard-content">
              {renderStepContent()}
            </div>
            {error && <div className="wizard-error">{error}</div>}
            {renderFooter()}
          </>
        )}
      </div>
    </div>
  )
}

export default AsistenteFinancieroInteligente