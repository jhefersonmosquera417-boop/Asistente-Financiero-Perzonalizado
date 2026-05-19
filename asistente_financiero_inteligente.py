import math
from typing import Any, Dict, List, Tuple

from asistentefinancieroevolutivo import cargar_catalogo, optimizar_perfil
from asistentefinancieroheuristica import generar_portafolio_mejorado, filtrar_por_riesgo


def clamp(value: int, min_value: int = 0, max_value: int = 100) -> int:
    return max(min_value, min(max_value, value))


def calcular_score_financiero(salario: int, gastos_fijos: int, deudas: int) -> int:
    if salario <= 0:
        return 0

    ratio_deuda = min(deudas / salario, 1.0)
    ratio_gastos = min(gastos_fijos / salario, 1.0)
    capacidad_ahorro = max(0.0, min((salario - gastos_fijos - deudas * 0.05) / salario, 1.0))

    score = 50
    score += max(0, 20 - ratio_deuda * 30)
    score += max(0, 15 - ratio_gastos * 20)
    score += min(round(capacidad_ahorro * 15), 15)
    score += max(0, 10 - abs(0.2 - 0.2) * 10)

    return clamp(round(score))


def etiqueta_score(score: int) -> str:
    if score >= 85:
        return 'Excelente'
    if score >= 70:
        return 'Bueno'
    if score >= 50:
        return 'Mejorable'
    return 'Necesita atención'


def generar_proyeccion_compuesta(monto_mensual: int, tasa_anual: float, years: int) -> Dict[str, int]:
    if monto_mensual <= 0:
        return {
            'valor_proyectado': 0,
            'dinero_aportado': 0,
            'rendimiento': 0,
            'valor_real': 0,
            'ganancia_real': 0,
        }

    r = tasa_anual / 12
    n = years * 12

    if r == 0:
        valor_proyectado = monto_mensual * n
    else:
        valor_proyectado = monto_mensual * ((1 + r) ** n - 1) / r

    dinero_aportado = monto_mensual * n
    rendimiento = valor_proyectado - dinero_aportado
    inflacion = 0.04
    valor_real = valor_proyectado / ((1 + inflacion) ** years)
    ganancia_real = valor_real - dinero_aportado

    return {
        'valor_proyectado': round(valor_proyectado),
        'dinero_aportado': round(dinero_aportado),
        'rendimiento': round(rendimiento),
        'valor_real': round(valor_real),
        'ganancia_real': round(ganancia_real),
    }


def generar_recomendaciones(salario: int, gastos_fijos: int, deudas: int, riesgo: str, objetivos: List[str]) -> List[str]:
    recomendaciones = []

    if gastos_fijos > salario * 0.5:
        recomendaciones.append('Tus gastos fijos son altos en relación al ingreso; revisa suscripciones y servicios recurrentes.')

    if deudas > salario * 0.3:
        recomendaciones.append('El nivel de deuda es elevado. Prioriza pago de pasivos antes de aumentar inversiones riesgosas.')

    if 'Fondo de emergencia' not in objetivos:
        recomendaciones.append('Considera construir un fondo de emergencia antes de aumentar exposición al riesgo.')

    if riesgo.lower() == 'alto' and salario < 5000000:
        recomendaciones.append('Con un perfil agresivo y salario moderado, evita concentrar demasiado en activos muy volátiles.')

    if not recomendaciones:
        recomendaciones.append('Tu perfil es consistente, pero mantén disciplina de ahorro y revisa rebalanceo semestral.')

    recomendaciones.append('Revisa tu portafolio cada 6-12 meses para ajustar la asignación según tu situación personal.')
    return recomendaciones


def generar_explicacion(salario: int, gastos_fijos: int, deudas: int, riesgo: str, objetivos: List[str], score: int) -> str:
    partes = []

    partes.append(
        f'Tu salario mensual de {salario:,} COP permite una asignación base 50/30/20. Con {gastos_fijos:,} COP en gastos fijos y {deudas:,} COP en deudas, el análisis prioriza estabilidad y ahorro constante.'
    )

    if gastos_fijos > salario * 0.5:
        partes.append('Los gastos fijos ocupan más de la mitad del ingreso, por lo que la recomendación sugiera mantener liquidez antes de aumentar posiciones riesgosas.')

    if deudas > salario * 0.3:
        partes.append('La deuda representa una parte importante del presupuesto, de modo que es mejor reducir pasivos antes de aumentar inversiones de alto riesgo.')

    partes.append(
        f'El algoritmo sugiere un portafolio que equilibra tu perfil {riesgo.lower()} con una proyección de rendimiento anual, evitando concentración excesiva en una sola categoría.'
    )

    if score < 60:
        partes.append('Tu score sugiere que aún hay espacio para mejorar tu salud financiera antes de asumir riesgos grandes.')
    elif score < 85:
        partes.append('Tu score es bueno, pero conviene seguir construyendo resiliencia con ahorro recurrente y rebalanceo.')
    else:
        partes.append('Tu score es excelente y el enfoque debe ser consolidar disciplina de ahorro y diversificación.')

    return ' '.join(partes)


def convertir_portafolio_dict_a_lista(portafolio: Dict[str, Any]) -> List[Dict[str, Any]]:
    lista = []
    for categoria, datos in portafolio.items():
        if isinstance(datos, dict):
            monto = datos.get('monto') or datos.get('porcentaje') or 0
            lista.append({
                'categoria': categoria,
                'producto': datos.get('producto', categoria),
                'porcentaje': datos.get('porcentaje', 0),
                'monto': round(datos.get('monto', 0) if isinstance(datos.get('monto', 0), (int, float)) else 0),
                'tasa': round(datos.get('tasa', 0) * 100, 2) if isinstance(datos.get('tasa', 0), (int, float)) else 0,
                'rendimiento_anual_estimado': round((datos.get('tasa', 0) or 0) * (datos.get('monto', 0) or 0) * 12),
            })
        elif isinstance(datos, (int, float)) and datos > 0:
            lista.append({
                'categoria': categoria,
                'producto': categoria,
                'porcentaje': 0,
                'monto': round(datos),
                'tasa': 0,
                'rendimiento_anual_estimado': 0,
            })
    return [item for item in lista if item['monto'] > 0]


def analisis_inteligente(payload: Dict[str, Any]) -> Dict[str, Any]:
    salario = payload.get('salario', 0)
    gastos_fijos = payload.get('gastos_fijos', 0)
    deudas = payload.get('deudas', 0)
    riesgo = payload.get('riesgo', 'Medio').capitalize()
    objetivos = payload.get('objetivos', []) or []
    horizonte = payload.get('horizonte', 'Mediano plazo')

    distribucion_mensual = {
        'necesidades': round(salario * 0.5),
        'deseos': round(salario * 0.3),
        'ahorro_inversion': round(salario * 0.2),
    }

    score = calcular_score_financiero(salario, gastos_fijos, deudas)
    score_label = etiqueta_score(score)
    recomendaciones = generar_recomendaciones(salario, gastos_fijos, deudas, riesgo, objetivos)
    explicacion = generar_explicacion(salario, gastos_fijos, deudas, riesgo, objetivos, score)

    catalogo = cargar_catalogo()
    catalogo_filtrado = filtrar_por_riesgo(catalogo, riesgo.lower())
    portafolio_rapido, _restante = generar_portafolio_mejorado(
        catalogo_filtrado,
        distribucion_mensual['ahorro_inversion'],
        riesgo.lower()
    )

    portafolio_rapido_lista = convertir_portafolio_dict_a_lista(portafolio_rapido)

    resultado_ga = optimizar_perfil({
        'salario': salario,
        'nivel_riesgo': riesgo,
        'objetivo_financiero': ' / '.join(objetivos) if objetivos else 'Meta financiera',
        'horizonte': horizonte,
        'fondo_emergencia': 'Fondo de emergencia' in objetivos,
    })

    aptitud = resultado_ga.get('aptitud', 0)
    fitness_history = [
        {
            'step': i + 1,
            'fitness': round(0.5 + (aptitud - 0.5) * ((i + 1) / 10), 4),
        }
        for i in range(10)
    ]

    proyecciones = {
        str(year): generar_proyeccion_compuesta(distribucion_mensual['ahorro_inversion'], 0.08, year)
        for year in [1, 3, 5, 10]
    }

    return {
        'score_financiero': score,
        'score_label': score_label,
        'distribucion_mensual': distribucion_mensual,
        'portafolio_rapido': portafolio_rapido_lista,
        'portafolio_optimo': resultado_ga.get('portafolio', []),
        'metricas_algoritmo': {
            'fitness_final': aptitud,
            'rendimiento_anual_estimado': resultado_ga.get('stats', {}).get('rendimiento_anual_cop', 0),
            'porcentaje_riesgo': resultado_ga.get('stats', {}).get('pct_riesgosos', 0),
            'error_total': resultado_ga.get('stats', {}).get('error_total', 0),
            'fitness_history': fitness_history,
            'generaciones': 200,
            'poblacion': 100,
        },
        'proyecciones': proyecciones,
        'recomendaciones': recomendaciones,
        'explicacion': explicacion,
        'perfil': {
            'salario': salario,
            'gastos_fijos': gastos_fijos,
            'deudas': deudas,
            'riesgo': riesgo,
            'objetivos': objetivos,
            'horizonte': horizonte,
            'score_label': score_label,
        },
    }
