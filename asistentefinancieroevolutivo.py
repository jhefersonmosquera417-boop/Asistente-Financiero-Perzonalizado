import random
import copy
from collections import Counter

perfil_usuario = {
    "salario":           1750000,
    "nivel_riesgo":      "Medio",
    "ahorro_inversion":   350000,
    "necesidades":        875000,
    "deseos":             525000,

    # Metas de distribución del portafolio (porcentajes objetivo)
    # El AG buscará acercarse lo más posible a estos valores.
    "distribucion_objetivo": {
        "cdt":             60,
        "fondos":          30,
        "acciones":         0,
        "criptomonedas":    0,
        "oro":              5,
        "emprendimientos":  5,
    },

    # Restricciones duras
    "max_activos_riesgosos": 10,     # % máximo en cripto+emprendimientos si salario < 2 SMMLV
    "smmlv":               1750905,  # Salario mínimo Colombia 2026
    "fondo_emergencia_meses": 3,
}




catalogo_inversiones = {
    "cdt": [
        {"id": "CDT1",  "entidad": "Bancolombia",         "tasa": 0.112, "riesgo": "bajo",  "minimo": 100000},
        {"id": "CDT2",  "entidad": "Davivienda",           "tasa": 0.110, "riesgo": "bajo",  "minimo": 150000},
        {"id": "CDT3",  "entidad": "BBVA",                 "tasa": 0.109, "riesgo": "bajo",  "minimo": 200000},
        {"id": "CDT4",  "entidad": "Banco de Bogotá",      "tasa": 0.111, "riesgo": "bajo",  "minimo": 100000},
        {"id": "CDT5",  "entidad": "Banco Popular",        "tasa": 0.108, "riesgo": "bajo",  "minimo": 100000},
        {"id": "CDT6",  "entidad": "Banco AV Villas",      "tasa": 0.107, "riesgo": "bajo",  "minimo": 100000},
        {"id": "CDT7",  "entidad": "Banco Caja Social",    "tasa": 0.113, "riesgo": "bajo",  "minimo":  50000},
        {"id": "CDT8",  "entidad": "Banco Itaú",           "tasa": 0.114, "riesgo": "bajo",  "minimo": 100000},
        {"id": "CDT9",  "entidad": "Scotiabank Colpatria", "tasa": 0.115, "riesgo": "bajo",  "minimo": 150000},
        {"id": "CDT10", "entidad": "Banco Falabella",      "tasa": 0.116, "riesgo": "bajo",  "minimo":  50000},
        {"id": "CDT11", "entidad": "Bancoomeva",           "tasa": 0.109, "riesgo": "bajo",  "minimo": 100000},
        {"id": "CDT12", "entidad": "Serfinanza",           "tasa": 0.118, "riesgo": "bajo",  "minimo":  50000},
        {"id": "CDT13", "entidad": "Finandina",            "tasa": 0.119, "riesgo": "bajo",  "minimo": 100000},
        {"id": "CDT14", "entidad": "Mibanco",              "tasa": 0.117, "riesgo": "bajo",  "minimo":  50000},
        {"id": "CDT15", "entidad": "Banco W",              "tasa": 0.120, "riesgo": "bajo",  "minimo":  50000},
    ],
    "fondos": [
        {"id": "F1",  "nombre": "Fondo Balanceado A",         "tasa": 0.135, "riesgo": "medio", "minimo":  50000},
        {"id": "F2",  "nombre": "Fondo Balanceado B",         "tasa": 0.132, "riesgo": "medio", "minimo":  50000},
        {"id": "F3",  "nombre": "Fondo Renta Mixta",          "tasa": 0.138, "riesgo": "medio", "minimo": 100000},
        {"id": "F4",  "nombre": "Fondo Moderado Plus",        "tasa": 0.140, "riesgo": "medio", "minimo":  80000},
        {"id": "F5",  "nombre": "Fondo Conservador Pro",      "tasa": 0.130, "riesgo": "medio", "minimo":  50000},
        {"id": "F6",  "nombre": "Fondo Global LATAM",         "tasa": 0.142, "riesgo": "medio", "minimo": 100000},
        {"id": "F7",  "nombre": "Fondo Indexado COLCAP",      "tasa": 0.145, "riesgo": "medio", "minimo":  70000},
        {"id": "F8",  "nombre": "Fondo Crecimiento",          "tasa": 0.150, "riesgo": "medio", "minimo": 120000},
        {"id": "F9",  "nombre": "Fondo Estrategia Dinámica",  "tasa": 0.148, "riesgo": "medio", "minimo":  90000},
        {"id": "F10", "nombre": "Fondo Renta Variable Local", "tasa": 0.152, "riesgo": "medio", "minimo": 100000},
        {"id": "F11", "nombre": "Fondo Internacional USD",    "tasa": 0.149, "riesgo": "medio", "minimo": 150000},
        {"id": "F12", "nombre": "Fondo ESG Colombia",         "tasa": 0.137, "riesgo": "medio", "minimo":  80000},
        {"id": "F13", "nombre": "Fondo Multiactivos",         "tasa": 0.141, "riesgo": "medio", "minimo":  60000},
        {"id": "F14", "nombre": "Fondo Renta Fija Plus",      "tasa": 0.128, "riesgo": "medio", "minimo":  50000},
        {"id": "F15", "nombre": "Fondo Estrategia Andina",    "tasa": 0.146, "riesgo": "medio", "minimo": 100000},
    ],
    "acciones": [
        {"id": "A1",  "empresa": "Ecopetrol",      "tasa": 0.180, "riesgo": "alto", "minimo": 20000},
        {"id": "A2",  "empresa": "Bancolombia",     "tasa": 0.170, "riesgo": "alto", "minimo": 20000},
        {"id": "A3",  "empresa": "Grupo Sura",      "tasa": 0.190, "riesgo": "alto", "minimo": 20000},
        {"id": "A4",  "empresa": "ISA",             "tasa": 0.160, "riesgo": "alto", "minimo": 20000},
        {"id": "A5",  "empresa": "Celsia",          "tasa": 0.200, "riesgo": "alto", "minimo": 20000},
        {"id": "A6",  "empresa": "Grupo Argos",     "tasa": 0.185, "riesgo": "alto", "minimo": 20000},
        {"id": "A7",  "empresa": "Nutresa",         "tasa": 0.175, "riesgo": "alto", "minimo": 20000},
        {"id": "A8",  "empresa": "Almacenes Éxito", "tasa": 0.165, "riesgo": "alto", "minimo": 20000},
        {"id": "A9",  "empresa": "Terpel",          "tasa": 0.182, "riesgo": "alto", "minimo": 20000},
        {"id": "A10", "empresa": "Canacol Energy",  "tasa": 0.195, "riesgo": "alto", "minimo": 20000},
    ],
    "criptomonedas": [
        {"id": "C1",  "token": "Bitcoin",   "tasa": 0.30, "riesgo": "alto", "minimo": 10000},
        {"id": "C2",  "token": "Ethereum",  "tasa": 0.28, "riesgo": "alto", "minimo": 10000},
        {"id": "C3",  "token": "Solana",    "tasa": 0.35, "riesgo": "alto", "minimo": 10000},
        {"id": "C4",  "token": "Cardano",   "tasa": 0.25, "riesgo": "alto", "minimo": 10000},
        {"id": "C5",  "token": "Polygon",   "tasa": 0.27, "riesgo": "alto", "minimo": 10000},
        {"id": "C6",  "token": "Chainlink", "tasa": 0.29, "riesgo": "alto", "minimo": 10000},
        {"id": "C7",  "token": "Avalanche", "tasa": 0.33, "riesgo": "alto", "minimo": 10000},
        {"id": "C8",  "token": "Litecoin",  "tasa": 0.22, "riesgo": "alto", "minimo": 10000},
        {"id": "C9",  "token": "Polkadot",  "tasa": 0.31, "riesgo": "alto", "minimo": 10000},
        {"id": "C10", "token": "Uniswap",   "tasa": 0.34, "riesgo": "alto", "minimo": 10000},
    ],
    "oro": [
        {"id": "ORO1", "nombre": "Oro físico (gramo)",     "tasa": 0.08, "riesgo": "bajo",  "minimo": 50000},
        {"id": "ORO2", "nombre": "ETF Oro SPDR",           "tasa": 0.09, "riesgo": "bajo",  "minimo": 30000},
        {"id": "ORO3", "nombre": "Plata física (gramo)",   "tasa": 0.07, "riesgo": "bajo",  "minimo": 20000},
        {"id": "ORO4", "nombre": "Fondo de metales LATAM", "tasa": 0.10, "riesgo": "medio", "minimo": 80000},
    ],
    "emprendimientos": [
        {"id": "E1", "nombre": "Microempresa comercio local",  "tasa": 0.25, "riesgo": "alto", "minimo": 100000},
        {"id": "E2", "nombre": "Venta digital / dropshipping", "tasa": 0.22, "riesgo": "alto", "minimo":  50000},
        {"id": "E3", "nombre": "Franquicia pequeña",           "tasa": 0.20, "riesgo": "alto", "minimo": 200000},
        {"id": "E4", "nombre": "Negocio de servicios",         "tasa": 0.18, "riesgo": "alto", "minimo":  80000},
    ],
}




def filtrar_catalogo_por_riesgo(catalogo, nivel_riesgo):
    """
    PURGA GENÉTICA: Antes de que empiece la evolución,
    limpiamos el pool genético de activos no permitidos.

      Nivel Bajo  → solo activos 'bajo'
      Nivel Medio → activos 'bajo' y 'medio'
      Nivel Alto  → todos los activos
    """
    niveles = {"bajo": 1, "medio": 2, "alto": 3}
    nivel_num = niveles.get(nivel_riesgo.lower(), 2)

    catalogo_limpio = {}
    for categoria, productos in catalogo.items():
        filtrados = [
            p for p in productos
            if niveles[p["riesgo"]] <= nivel_num
        ]
        if filtrados:
            catalogo_limpio[categoria] = filtrados

    return catalogo_limpio


# Ejecutamos la purga UNA SOLA VEZ antes de que arranque el AG
catalogo_seguro = filtrar_catalogo_por_riesgo(
    catalogo_inversiones,
    perfil_usuario["nivel_riesgo"]
)




TAMANO_POBLACION = 100   # Portafolios compitiendo en cada generación
GENERACIONES     = 150   # Ciclos de evolución
TASA_MUTACION    = 0.15  # 15% de probabilidad de mutación




def crear_individuo():
    """
    GÉNESIS: Crea un individuo (cromosoma).

    Un individuo es un portafolio: diccionario donde cada
    categoría disponible tiene un producto elegido al azar
    y un porcentaje de asignación normalizado a 100%.

    Ejemplo de individuo:
    {
      "cdt":    {"producto": {id:"CDT7",...}, "porcentaje": 62.3},
      "fondos": {"producto": {id:"F8",...},   "porcentaje": 32.4},
      "oro":    {"producto": {id:"ORO2",...}, "porcentaje": 5.3},
    }
    """
    categorias   = list(catalogo_seguro.keys())
    pesos_brutos = [random.uniform(5, 60) for _ in categorias]
    total        = sum(pesos_brutos)
    individuo    = {}

    for i, cat in enumerate(categorias):
        individuo[cat] = {
            "producto":   random.choice(catalogo_seguro[cat]),
            "porcentaje": round((pesos_brutos[i] / total) * 100, 1)
        }

    _normalizar_porcentajes(individuo)
    return individuo


def _normalizar_porcentajes(individuo):
    """Ajusta porcentajes para que sumen exactamente 100."""
    total = sum(v["porcentaje"] for v in individuo.values())
    if total == 0:
        return
    factor = 100.0 / total
    keys   = list(individuo.keys())
    for k in keys:
        individuo[k]["porcentaje"] = round(individuo[k]["porcentaje"] * factor, 1)
    # Corrección del redondeo en el último elemento
    diff = 100.0 - sum(individuo[k]["porcentaje"] for k in keys)
    individuo[keys[-1]]["porcentaje"] = round(
        individuo[keys[-1]]["porcentaje"] + diff, 1
    )




def evaluar_aptitud(individuo, perfil):
    """
    EL JUEZ (Fitness): ¿Qué tan bueno es este portafolio?

    Maximiza : rendimiento esperado anual en COP
    Penaliza (castigos):
      R1 - Exceder límite de activos riesgosos (salario < 2 SMMLV)
      R2 - Desviarse de la distribución objetivo del perfil
      R3 - Concentrar más del 50% en una sola categoría
      R4 - Incluir activos cuyo mínimo supera el monto asignado
    """
    ahorro        = perfil["ahorro_inversion"]
    objetivo      = perfil["distribucion_objetivo"]
    nivel_riesgo  = perfil["nivel_riesgo"].lower()
    salario       = perfil["salario"]
    smmlv         = perfil["smmlv"]
    max_riesgosos = perfil["max_activos_riesgosos"]

    rendimiento_total = 0.0
    error_total       = 0.0
    pct_riesgosos     = 0.0

    # --- FASE 1: RECOLECCIÓN DE MÉTRICAS ---
    for cat, datos in individuo.items():
        pct    = datos["porcentaje"]
        tasa   = datos["producto"]["tasa"]
        minimo = datos["producto"]["minimo"]
        monto  = (pct / 100) * ahorro

        rendimiento_total += monto * tasa

        if datos["producto"]["riesgo"] == "alto":
            pct_riesgosos += pct

        # R4: Castigo si el mínimo del producto supera el monto asignado
        if monto < minimo:
            error_total += (minimo - monto) * 0.5

    # --- R1: Límite de activos riesgosos ---
    if salario < (2 * smmlv):
        exceso = max(0, pct_riesgosos - max_riesgosos)
        error_total += exceso * 2000

    # --- R2: Desviación respecto a distribución objetivo ---
    for cat, pct_meta in objetivo.items():
        pct_real   = individuo.get(cat, {}).get("porcentaje", 0)
        desviacion = abs(pct_real - pct_meta)
        error_total += desviacion * 500

    # --- R3: Penalizar concentración excesiva (> 50% en una sola categoría) ---
    for cat, datos in individuo.items():
        if datos["porcentaje"] > 50:
            error_total += (datos["porcentaje"] - 50) * 1000

    # --- FASE 2: APTITUD FINAL ---
    # Fórmula inversa idéntica a la del profesor:
    # mayor error → menor aptitud; rendimiento actúa como bonificación base
    aptitud = (rendimiento_total + 1) / (1 + error_total)

    stats = {
        "rendimiento_anual_cop": round(rendimiento_total),
        "pct_riesgosos":         round(pct_riesgosos, 1),
        "error_total":           round(error_total, 2),
    }

    return aptitud, stats




def seleccion_torneo(poblacion):
    """
    SELECCIÓN NATURAL: Torneo de 4 candidatos.
    Tomamos 4 portafolios al azar → gana el de mayor aptitud.
    (Igual que en los ejemplos del profesor)
    """
    torneo = random.sample(poblacion, 4)
    torneo.sort(
        key=lambda ind: evaluar_aptitud(ind, perfil_usuario)[0],
        reverse=True
    )
    return copy.deepcopy(torneo[0])


def cruzar(padre1, padre2):
    """
    REPRODUCCIÓN (Crossover):
    Punto de cruce aleatorio sobre las categorías del portafolio.
    Antes del corte → genes del padre1.
    Después del corte → genes del padre2.
    (Mismo mecanismo del profesor, adaptado a categorías financieras)
    """
    hijo       = {}
    categorias = list(padre1.keys())
    punto_cruce = random.randint(1, len(categorias) - 1)

    for i, cat in enumerate(categorias):
        if i < punto_cruce:
            hijo[cat] = copy.deepcopy(padre1[cat])
        else:
            hijo[cat] = copy.deepcopy(padre2.get(cat, padre1[cat]))

    _normalizar_porcentajes(hijo)
    return hijo


def mutar(individuo):
    """
    MUTACIÓN: 15% de probabilidad de cambiar UN gen.

    Tipo A (producto):    reemplaza el instrumento dentro de una categoría
    Tipo B (porcentaje):  redistribuye aleatoriamente las asignaciones
    (Igual en espíritu al mutar() del profesor)
    """
    if random.random() < TASA_MUTACION:
        categorias  = list(individuo.keys())
        cat_elegida = random.choice(categorias)
        tipo        = random.choice(["producto", "porcentaje"])

        if tipo == "producto":
            individuo[cat_elegida]["producto"] = random.choice(
                catalogo_seguro.get(cat_elegida,
                                    [individuo[cat_elegida]["producto"]])
            )
        else:
            pesos = [random.uniform(5, 60) for _ in categorias]
            total = sum(pesos)
            for i, cat in enumerate(categorias):
                individuo[cat]["porcentaje"] = round((pesos[i] / total) * 100, 1)
            _normalizar_porcentajes(individuo)

    return individuo




def main():
    print("=" * 62)
    print("  ASISTENTE FINANCIERO PERSONALIZADO - COLOMBIA")
    print("  MÓDULO 4: HEURÍSTICA EVOLUTIVA (ALGORITMO GENÉTICO)")
    print("=" * 62)

    print(f"\nPerfil cargado:")
    print(f"  Salario:          ${perfil_usuario['salario']:,} COP")
    print(f"  Nivel de riesgo:  {perfil_usuario['nivel_riesgo']}")
    print(f"  Ahorro/Inversión: ${perfil_usuario['ahorro_inversion']:,} COP/mes")

    print(f"\nCatálogo filtrado para riesgo '{perfil_usuario['nivel_riesgo']}':")
    for cat, prods in catalogo_seguro.items():
        print(f"  {cat:<18}: {len(prods)} productos disponibles")

    print(f"\nParámetros del AG:")
    print(f"  Población:    {TAMANO_POBLACION} individuos")
    print(f"  Generaciones: {GENERACIONES} ciclos")
    print(f"  Mutación:     {int(TASA_MUTACION*100)}%")
    print("\nIniciando evolución...\n")

    # --- 5.1 POBLACIÓN CERO ---
    # 100 portafolios iniciales caóticos y aleatorios
    poblacion = [crear_individuo() for _ in range(TAMANO_POBLACION)]

    mejor_historico         = None
    mejor_aptitud_historica = -1
    mejores_stats           = {}

    # --- 5.2 EL PASO DEL TIEMPO ---
    for generacion in range(GENERACIONES):
        nueva_poblacion = []

        # Evaluamos toda la población actual
        poblacion_evaluada = [
            (ind, evaluar_aptitud(ind, perfil_usuario))
            for ind in poblacion
        ]
        # Ordenamos de mayor a menor aptitud
        poblacion_evaluada.sort(key=lambda x: x[1][0], reverse=True)

        # --- ELITISMO ---
        # El campeón pasa DIRECTAMENTE sin ser modificado
        mejor_actual, (aptitud_actual, stats_actual) = poblacion_evaluada[0]
        nueva_poblacion.append(mejor_actual)

        # ¿Es el mejor de toda la historia?
        if aptitud_actual > mejor_aptitud_historica:
            mejor_historico         = copy.deepcopy(mejor_actual)
            mejor_aptitud_historica = aptitud_actual
            mejores_stats           = stats_actual

        # Progreso cada 25 generaciones
        if (generacion + 1) % 25 == 0:
            print(f"  Gen {generacion+1:>3} | "
                  f"Aptitud: {aptitud_actual:.4f} | "
                  f"Rendimiento: ${stats_actual['rendimiento_anual_cop']:,} COP/año")

        # --- REPRODUCCIÓN ---
        while len(nueva_poblacion) < TAMANO_POBLACION:
            padre1 = seleccion_torneo(poblacion)
            padre2 = seleccion_torneo(poblacion)
            hijo   = cruzar(padre1, padre2)
            hijo   = mutar(hijo)
            nueva_poblacion.append(hijo)

        poblacion = nueva_poblacion

 

    ahorro = perfil_usuario["ahorro_inversion"]

    print("\n" + "=" * 62)
    print("  PORTAFOLIO ÓPTIMO ENCONTRADO  →  RESPUESTA 100%")
    print("=" * 62)

    print(f"\n1. Distribución mensual (Regla 50/30/20):")
    print(f"   Necesidades:      ${perfil_usuario['necesidades']:>10,} COP  (50%)")
    print(f"   Deseos:           ${perfil_usuario['deseos']:>10,} COP  (30%)")
    print(f"   Ahorro/Inversión: ${ahorro:>10,} COP  (20%)")

    print(f"\n2. Portafolio optimizado por Algoritmo Genético:")
    cabecera = f"   {'Categoría':<18} {'Instrumento':<32} {'%':>6}  {'Monto':>12}  {'Tasa':>6}"
    print(cabecera)
    print("   " + "-" * 76)

    rendimiento_total = 0.0
    for cat, datos in mejor_historico.items():
        prod   = datos["producto"]
        pct    = datos["porcentaje"]
        monto  = round((pct / 100) * ahorro)
        tasa   = prod["tasa"]
        rend   = monto * tasa
        rendimiento_total += rend
        nombre = (prod.get("entidad") or prod.get("nombre")
                  or prod.get("empresa") or prod.get("token", ""))
        print(f"   {cat:<18} {nombre:<32} {pct:>5.1f}%  ${monto:>11,}  {tasa*100:>5.1f}%")

    print("   " + "-" * 76)
    print(f"   {'TOTAL':<18} {'':<32} {'100.0':>5}%  ${ahorro:>11,}")

    print(f"\n3. Proyección a 12 meses:")
    capital_12 = ahorro * 12
    valor_proyectado = capital_12 + rendimiento_total
    print(f"   Capital mensual invertido:  ${ahorro:>12,} COP")
    print(f"   Capital total en 12 meses:  ${capital_12:>12,} COP")
    print(f"   Rendimiento anual estimado: ${rendimiento_total:>12,.0f} COP")
    print(f"   Valor proyectado total:     ${valor_proyectado:>12,.0f} COP")
    print(f"   % activos riesgosos:        {mejores_stats['pct_riesgosos']}%")

    print(f"\n4. Fondo de emergencia recomendado:")
    fondo = perfil_usuario["salario"] * perfil_usuario["fondo_emergencia_meses"]
    print(f"   {perfil_usuario['fondo_emergencia_meses']} meses × "
          f"${perfil_usuario['salario']:,} = ${fondo:,} COP")
    print(f"   (Acumular ANTES de invertir en activos de baja liquidez)")

    print(f"\n{'─' * 62}")
    print("  ADVERTENCIA: Simulación con fines educativos.")
    print("  No constituye asesoría financiera legal ni profesional.")
    print(f"{'─' * 62}\n")


# ==========================================================
# PUNTO DE ENTRADA
# ==========================================================
if __name__ == "__main__":
    main()
