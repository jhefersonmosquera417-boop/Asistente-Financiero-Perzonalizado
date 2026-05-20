import datasetRaw from './dataset_catalogo_inversiones.jsonl?raw';

// Cargamos y mapeamos el catálogo en memoria para tener acceso rápido a las características
const catalogoInversiones = datasetRaw
  .split('\n')
  .map(line => line.trim())
  .filter(line => line.length > 0)
  .map(line => {
    try {
      return JSON.parse(line);
    } catch (e) {
      console.error("Error parseando línea del dataset:", line, e);
      return null;
    }
  })
  .filter(item => item !== null);

export function mapearPortafolioConProductos(portafolioOptimo, datosPerfil) {
  if (!portafolioOptimo || portafolioOptimo.length === 0) {
    return [];
  }

  // Ahora el portafolio del backend ya trae los productos reales identificados por ID
  return portafolioOptimo.map(item => {
    // Buscamos en nuestro catálogo si el producto tiene características detalladas guardadas
    const productoCatalogo = catalogoInversiones.find(prod => prod.id === item.id);

    // Ajustamos las características dinámicas o dejamos unas por defecto reales
    const caracteristicasFinales = productoCatalogo?.caracteristicas || [
      `Inversión regulada en la categoría de ${item.categoria.toUpperCase()}`,
      `Monto mínimo de entrada: $${(item.minimo || 0).toLocaleString('es-CO')} COP`,
      'Disponible para inversionistas en Colombia a través de canales digitales'
    ];

    // Construimos la justificación de negocio real basada en la optimización del backend
    const rentabilidadFormateada = (item.tasa * 100).toFixed(1);
    const justificacionReal = `El algoritmo genético asignó un ${(item.porcentaje)}% de tu capital aquí porque supera el umbral mínimo exigido de $${(item.minimo || 0).toLocaleString('es-CO')} COP y optimiza tu rentabilidad esperada al ${rentabilidadFormateada}% E.A. bajo un nivel de riesgo ${item.riesgo}.`;

    return {
      categoria: item.categoria,
      porcentaje: item.porcentaje,
      monto_mensual: item.monto_mensual,
      producto: {
        nombre: item.nombre || `Producto ${item.id}`,
        rentabilidad_anual: item.tasa,
        riesgo: item.riesgo ? (item.riesgo.charAt(0).toUpperCase() + item.riesgo.slice(1)) : 'Medio',
        liquidez: item.categoria === 'cdt' ? 'Baja (Plazo Fijo)' : 'Alta',
        monto_minimo: item.minimo || 0,
        caracteristicas: caracteristicasFinales
      },
      justificacion: justificacionReal
    };
  });
}

export function generarAnalisisPersonalizado(datosPerfil, data) {
  const { salario, gastos_fijos, deudas, riesgo, horizonte } = datosPerfil;
  const salarioNum = Number(salario) || 0;
  const gastosNum = Number(gastos_fijos) || 0;
  const deudasNum = Number(deudas) || 0;

  const SMMLV_2026 = 1750905; 
  const ganaMenosDelMinimo = salarioNum < SMMLV_2026;

  const necesidades = Math.round(salarioNum * 0.5);
  const deseos = Math.round(salarioNum * 0.3);
  const ahorroInversion = Math.round(salarioNum * 0.2);
  
  const endeudamiento = salarioNum > 0 ? ((gastosNum + deudasNum) / salarioNum) * 100 : 0;
  const capacidadLibre = Math.max(0, ahorroInversion - (gastosNum + deudasNum));
  const saludFinanciera = endeudamiento > 80 ? 'Crítica' : endeudamiento > 60 ? 'Preocupante' : 'Saludable';

  let seccionAlertaSalario = '';
  if (ganaMenosDelMinimo && salarioNum > 0) {
    seccionAlertaSalario = `
🚨 ALERTA DE SEGURIDAD PATRIMONIAL:
Tu salario registrado es menor al salario mínimo legal en Colombia ($1.750.905 COP). En tu situación actual, el algoritmo restringe la exposición directa a mercados volátiles de alto riesgo (Acciones o Criptomonedas). Tu prioridad financiera número uno no debe ser buscar rentabilidades variables especulativas, sino consolidar un Fondo de Emergencias (equivalente a un rango de 3 meses de tus gastos) en vehículos de riesgo extra-bajo y disponibilidad inmediata, como cuentas de ahorros de alta rentabilidad o CDTs digitales a corto plazo. Protege el dinero de tu sustento diario.
`;
  }

  return `
ANÁLISIS DE TU SITUACIÓN FINANCIERA:
${seccionAlertaSalario}
DISTRIBUCIÓN DEL SALARIO (REGLA 50/30/20)
Tu salario mensual de ${salarioNum.toLocaleString('es-CO')} COP se distribuye de la siguiente manera:
- Necesidades (50%): ${necesidades.toLocaleString('es-CO')} COP (Vivienda, alimentos, servicios básicos)
- Deseos (30%): ${deseos.toLocaleString('es-CO')} COP (Entretenimiento, hobbies, lujos)
- Ahorro e Inversión (20%): ${ahorroInversion.toLocaleString('es-CO')} COP (Tu capital para crecimiento patrimonial)

SALUD FINANCIERA Y ANÁLISIS DE ENDEUDAMIENTO
Relación: Gastos Fijos (${gastosNum.toLocaleString('es-CO')} COP) + Deudas (${deudasNum.toLocaleString('es-CO')} COP) = ${(gastosNum + deudasNum).toLocaleString('es-CO')} COP
- Porcentaje de endeudamiento: ${endeudamiento.toFixed(1)}% -> Estado: ${saludFinanciera}
- Capacidad de maniobra disponible: ${capacidadLibre.toLocaleString('es-CO')} COP ${capacidadLibre > 0 ? 'para invertir sin comprometer liquidez' : '(Revisar urgentemente)'}
${endeudamiento > 70 ? '\n⚠️ ALERTA POR ENDEUDAMIENTO: Tu endeudamiento es elevado. Prioriza reducir deudas antes de aumentar inversiones riesgosas.' : '✓ RATIO DE DEUDAS: Tu nivel de endeudamiento actual permite inversión estratégica.'}

PROTECCIÓN CONTRA CONCENTRACIÓN DE RIESGO (ALGORITMO GENÉTICO)
Con perfil ${riesgo.toLowerCase()} e horizonte ${horizonte.toLowerCase()}, el portafolio ha sido optimizado por algoritmo genético para:
- Minimizar riesgo sistémico: Solo ${riesgo === 'Bajo' || ganaMenosDelMinimo ? '0-5%' : riesgo === 'Medio' ? '25-35%' : '50%+'} en activos de alta volatilidad
- Mantener liquidez para emergencias: Mínimo 10% en activos de acceso inmediato
- Generar ingresos recurrentes: 60% del portafolio en bonos y fondos conservadores
- Permitir crecimiento: ${riesgo === 'Alto' && !ganaMenosDelMinimo ? '40%+' : riesgo === 'Medio' && !ganaMenosDelMinimo ? '15-30%' : '0-10%'} en acciones e ETF para inflación

CONCLUSIÓN ESTRATÉGICA
Este portafolio está diseñado para que NO vivas en estrés por fluctuaciones del mercado. 
${ganaMenosDelMinimo ? '🎯 Tu objetivo inmediato: Enfoque 100% en liquidez, ahorro de emergencia y protección del capital.' : endeudamiento > 70 ? '🎯 Tu objetivo inmediato: Reducir endeudamiento a menos del 60%. Luego, acelerar inversión.' : '🎯 Estás en posición de comenzar inversión inmediata según el plan recomendado.'}

---

⚠️ RESPONSABILIDAD Y AVISO LEGAL (DISCLAIMER):
Esta herramienta es un simulador educativo basado en un Algoritmo Genético de optimización y no constituye una asesoría financiera formal, captación de dinero ni recomendación de compra/venta de activos. Los rendimientos históricos mostrados de los productos reales (CDTs, FICs, Acciones, ETFs, Cripto) son de carácter meramente ilustrativo y no garantizan ganancias futures. Toda inversión conlleva riesgos inherentes de pérdida de capital parcial o total. Antes de tomar una decisión real, valida los términos, costos y comisiones vigentes directamente con las entidades financieras vigiladas por la Superintendencia Financiera de Colombia (SFC).
  `.trim();
}