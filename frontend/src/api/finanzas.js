export async function analisisInteligente(payload) {
  const response = await fetch('http://localhost:8000/analisis-inteligente', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail || 'Error al obtener análisis inteligente')
  }

  return response.json()
}
