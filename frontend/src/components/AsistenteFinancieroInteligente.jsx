import { useMemo, useState } from 'react'

import { optimizarPortafolioEvolutivo } from '../api/finanzas'
import './AsistenteFinancieroInteligente.css'

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

  const salarioNumber = Number(salario || 0)
  const gastosFijosNumber = Number(gastosFijos || 0)
  const deudasNumber = Number(deudas || 0)

  const distribucion = useMemo(() => ({
    necesidades: Math.round(salarioNumber * 0.5),
    deseos: Math.round(salarioNumber * 0.3),
    ahorro_inversion: Math.round(salarioNumber * 0.2),
  }), [salarioNumber])

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
      if (!salarioNumber || salarioNumber <= 0) return 'Ingresa un salario válido.'
      if (gastosFijosNumber < 0) return 'Gastos fijos no pueden ser negativos.'
      if (deudasNumber < 0) return 'Deudas no pueden ser negativas.'
    }

    if (step === 1 && !riesgo) {
      return 'Selecciona tu perfil de riesgo.'
    }

    if (step === 2 && objetivos.length === 0) {
      return 'Selecciona al menos un objetivo financiero.'
    }

    return ''
  }

  const avanzarPaso = () => {
    const validation = validarPaso()
    if (validation) {
      setError(validation)
      return
    }
    setError('')
    setStep((prev) => Math.min(prev + 1, pasos.length - 1))
  }

  const retrocederPaso = () => {
    if (step === 0) {
      onBack()
      return
    }
    setError('')
    setStep((prev) => Math.max(prev - 1, 0))
  }

  // 🚨 CAMBIO 2: Modificamos la función para disparar el Algoritmo Genético real
  const enviarAnalisis = async () => {
    setError('')
    setLoading(true)

    try {
      // Mapeo riguroso según la clase ConsultaFinanciera del main.py de tu backend
      const payload = {
        salario: salarioNumber,
        nivel_riesgo: riesgo, // 'Bajo', 'Medio', 'Alto'
        objetivo_financiero: objetivos.join(', '), // String plano requerido por Python
        horizonte: horizonteLabel, // 'Corto plazo', 'Mediano plazo', 'Largo plazo'
        fondo_emergencia: objetivos.includes('Fondo de emergencia') // Determina dinámicamente si se calcula o no
      }

      // Llamada directa al endpoint /analizar de FastAPI
      const response = await optimizarPortafolioEvolutivo(payload)
      
      // onComplete enviará la estructura de tipo RespuestaFinanciera al Dashboard principal
      onComplete(response)
    } catch (err) {
      setError(err.message || 'Error conectando con el motor genético Python.')
    } finally {
      setLoading(false)
    }
  }

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
                onChange={(event) => setSalario(event.target.value)}
                placeholder="Ej. 3500000"
              />
            </div>
            <div className="field-group">
              <label>Gastos fijos mensuales</label>
              <input
                type="number"
                value={gastosFijos}
                onChange={(event) => setGastosFijos(event.target.value)}
                placeholder="Ej. 1200000"
              />
            </div>
            <div className="field-group">
              <label>Deudas mensuales</label>
              <input
                type="number"
                value={deudas}
                onChange={(event) => setDeudas(event.target.value)}
                placeholder="Ej. 450000"
              />
            </div>
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
                <strong>Ahorro / inversión</strong>
                <span>{distribucion.ahorro_inversion.toLocaleString('es-CO')} COP</span>
              </div>
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
                  type="range"
                  min="1"
                  max="10"
                  value={horizonte}
                  onChange={(event) => setHorizonte(Number(event.target.value))}
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
              <strong>{salarioNumber.toLocaleString('es-CO')} COP</strong>
            </div>
            <div className="summary-row">
              <span>Gastos fijos</span>
              <strong>{gastosFijosNumber.toLocaleString('es-CO')} COP</strong>
            </div>
            <div className="summary-row">
              <span>Deudas</span>
              <strong>{deudasNumber.toLocaleString('es-CO')} COP</strong>
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
            <div className="preview-card compact">
              <span className="preview-title">Distribución mensual</span>
              <div className="preview-row">
                <strong>Necesidades</strong>
                <span>{distribucion.necesidades.toLocaleString('es-CO')} COP</span>
              </div>
              <div className="preview-row">
                <strong>Deseos</strong>
                <span>{distribucion.deseos.toLocaleString('es-CO')} COP</span>
              </div>
              <div className="preview-row">
                <strong>Ahorro / inversión</strong>
                <span>{distribucion.ahorro_inversion.toLocaleString('es-CO')} COP</span>
              </div>
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