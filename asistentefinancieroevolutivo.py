import json
import random
import copy

# ==================================================
# CARGA DE DATASETS
# ==================================================
RUTA_PERFILES = "dataset_finanzas_colombia.jsonl"
RUTA_CATALOGO = "dataset_catalogo_inversiones.jsonl"

def cargar_perfil():
    """Carga un perfil financiero aleatorio desde el dataset colombiano."""
    import re
    perfiles = []
    with open(RUTA_PERFILES, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            perfiles.append(json.loads(linea))

    perfil_raw = random.choice(perfiles)
    input_str = perfil_raw.get("input", "")
    salario_match = re.search(r'Salario:\s*(\d+)', input_str)
    riesgo_match = re.search(r'Riesgo:\s*(\w+)', input_str)

    salario = int(salario_match.group(1)) if salario_match else 2000000
    nivel_riesgo = riesgo_match.group(1).capitalize() if riesgo_match else "Medio"

    return {
        "salario": salario,
        "nivel_riesgo": nivel_riesgo,
        "ahorro_inversion": round(salario * 0.20),
        "necesidades": round(salario * 0.50),
        "deseos": round(salario * 0.30),
        "distribucion_objetivo": {
            "cdt": 60,
            "fondos": 35,
            "acciones": 5,
        },
        "max_activos_riesgosos": 10,
        "smmlv": 1750905,
        "fondo_emergencia_meses": 3,
    }

def cargar_catalogo():
    """Carga productos de inversión desde dataset_catalogo_inversiones.jsonl"""
    catalogo = {}
    try:
        with open(RUTA_CATALOGO, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                if not linea.strip():
                    continue
                item = json.loads(linea)
                categoria = item["categoria"].lower().strip() # Normalizamos a minúsculas

                # Mapeo defensivo de los campos del producto
                producto = {
                    "id": item.get("id"),
                    "riesgo": str(item.get("riesgo", "medio")).lower().strip(),
                    "tasa": float(item.get("tasa", 0.10)),
                    "minimo": float(item.get("minimo", 0)),
                    "liquidez": item.get("liquidez", "Alta"),
                    # Extraemos el nombre real según cómo venga en tu JSONL
                    "nombre": item.get("nombre") or item.get("entidad") or item.get("empresa") or item.get("token") or "Producto Inversión"
                }

                if categoria not in catalogo:
                    catalogo[categoria] = []
                catalogo[categoria].append(producto)
    except FileNotFoundError:
        print(f"⚠️ Error: No se encontró {RUTA_CATALOGO}")
    return catalogo

# Cargar datos del catálogo una sola vez en memoria
catalogo_inversiones = cargar_catalogo()

OBJETIVOS_BASE = {
    "bajo": {"cdt": 40, "fondos": 30, "bonos": 15, "etf": 10, "finca_raiz": 5, "acciones": 0, "criptomoneda": 0},
    "medio": {"cdt": 25, "fondos": 25, "bonos": 15, "etf": 15, "finca_raiz": 10, "acciones": 7, "criptomoneda": 3},
    "alto": {"cdt": 20, "fondos": 20, "bonos": 10, "etf": 15, "finca_raiz": 10, "acciones": 12, "criptomoneda": 13}
}

def generar_distribucion_objetivo(catalogo, nivel_riesgo):
    base = OBJETIVOS_BASE.get(nivel_riesgo.lower(), OBJETIVOS_BASE["medio"])
    objetivo = {}
    for categoria in catalogo:
        if categoria in base:
            objetivo[categoria] = base[categoria]
        else:
            objetivo[categoria] = 5.0

    total = sum(objetivo.values())
    if total <= 0:
        equal = 100.0 / len(objetivo)
        return {cat: round(equal, 1) for cat in objetivo}

    return {cat: round((peso / total) * 100, 1) for cat, peso in objetivo.items()}

def preparar_entorno_evolutivo(perfil_usuario):
    """Prepara el perfil calculando de manera segura los montos que falten."""
    salario = int(perfil_usuario.get("salario") or perfil_usuario.get("salarioMensual") or 2000000)
    nivel_riesgo = perfil_usuario.get("nivel_riesgo") or perfil_usuario.get("riesgo") or "Medio"
    fondo_emergencia = perfil_usuario.get("fondo_emergencia", True)
    horizonte = perfil_usuario.get("horizonte", "plazo medio")

    perfil = {
        "salario": salario,
        "nivel_riesgo": nivel_riesgo,
        "objetivo_financiero": perfil_usuario.get("objetivo_financiero", "mejorar mis finanzas"),
        "horizonte": horizonte,
        "fondo_emergencia": fondo_emergencia,
        "ahorro_inversion": round(salario * 0.20),
        "necesidades": round(salario * 0.50),
        "deseos": round(salario * 0.30),
        "smmlv": 1750905,
        "fondo_emergencia_meses": 3 if fondo_emergencia else 0,
    }

    catalogo_seguro = filtrar_catalogo_por_riesgo(catalogo_inversiones, nivel_riesgo)
    distribucion = generar_distribucion_objetivo(catalogo_seguro, nivel_riesgo)
    perfil["distribucion_objetivo"] = ajustar_distribucion_por_horizonte(distribucion, horizonte, nivel_riesgo)
    return perfil, catalogo_seguro

def ajustar_distribucion_por_horizonte(distribucion, horizonte, nivel_riesgo):
    meta = distribucion.copy()
    horizonte_bajo = str(horizonte).lower()

    if "largo" in horizonte_bajo:
        for categoria in ["acciones", "etf", "finca_raiz", "criptomoneda"]:
            if categoria in meta: meta[categoria] = meta.get(categoria, 0) + 4
        for categoria in ["cdt", "fondos", "bonos"]:
            if categoria in meta: meta[categoria] = max(0, meta.get(categoria, 0) - 3)
    elif "corto" in horizonte_bajo:
        for categoria in ["cdt", "fondos", "bonos"]:
            if categoria in meta: meta[categoria] = meta.get(categoria, 0) + 4
        for categoria in ["acciones", "etf", "criptomoneda"]:
            if categoria in meta: meta[categoria] = max(0, meta.get(categoria, 0) - 3)

    total = sum(meta.values())
    if total <= 0: return distribucion
    return {cat: round((peso / total) * 100, 1) for cat, peso in meta.items()}

def filtrar_catalogo_por_riesgo(catalogo, nivel_riesgo):
    niveles = {"bajo": 1, "medio": 2, "alto": 3}
    nivel_num = niveles.get(nivel_riesgo.lower(), 2)

    catalogo_limpio = {}
    for categoria, productos in catalogo.items():
        filtrados = [p for p in productos if niveles.get(p["riesgo"], 2) <= nivel_num]
        if filtrados:
            catalogo_limpio[categoria] = filtrados
    return catalogo_limpio

TAMANO_POBLACION = 100
GENERACIONES     = 200
TASA_MUTACION    = 0.20

def crear_individuo(perfil, catalogo_seguro):
    objetivo = perfil["distribucion_objetivo"]
    categorias = [cat for cat in objetivo if cat in catalogo_seguro]
    
    if not categorias:
        categorias = list(catalogo_seguro.keys())

    def peso_aleatorio(cat):
        objetivo_pct = objetivo.get(cat, 0) or 5
        return max(1.0, random.gauss(objetivo_pct, objetivo_pct * 0.25))

    pesos_brutos = [peso_aleatorio(cat) for cat in categorias]
    total = sum(pesos_brutos) if sum(pesos_brutos) > 0 else 1
    individuo = {}

    for i, cat in enumerate(categorias):
        individuo[cat] = {
            "producto": random.choice(catalogo_seguro[cat]),
            "porcentaje": round((pesos_brutos[i] / total) * 100, 1)
        }

    _normalizar_porcentajes(individuo)
    return individuo

def _normalizar_porcentajes(individuo):
    total = sum(v["porcentaje"] for v in individuo.values())
    if total == 0: return
    factor = 100.0 / total
    keys = list(individuo.keys())
    for k in keys:
        individuo[k]["porcentaje"] = round(individuo[k]["porcentaje"] * factor, 1)
    diff = 100.0 - sum(individuo[k]["porcentaje"] for k in keys)
    individuo[keys[-1]]["porcentaje"] = round(individuo[keys[-1]]["porcentaje"] + diff, 1)

def evaluar_aptitud(individuo, perfil):
    """Función Fitness: Castiga de forma implacable violaciones de mínimos (Mínimo global $50.000)."""
    ahorro = perfil["ahorro_inversion"]
    objetivo = perfil["distribucion_objetivo"]
    salario = perfil["salario"]

    rendimiento_total = 0.0
    error_total = 0.0
    pct_riesgosos = 0.0

    for cat, datos in individuo.items():
        pct = datos["porcentaje"]
        if pct <= 0: continue
        
        producto = datos["producto"]
        monto = (pct / 100) * ahorro

        rendimiento_total += monto * producto["tasa"]
        if producto["riesgo"] == "alto":
            pct_riesgosos += pct

        # 🚨 ESTABLECER MÍNIMO DE NEGOCIO (Mínimo $50.000 o lo que diga el JSONL, el mayor)
        minimo_real_requerido = max(50000.0, float(producto.get("minimo", 50000)))

        # 🚨 PENALIZACIÓN ULTRA SEVERA
        if monto < minimo_real_requerido:
            # Multiplicamos la tajada faltante por 100 y sumamos un castigo fijo. 
            # Esto sepulta el fitness de este portafolio por completo.
            error_total += (minimo_real_requerido - monto) * 100 + 500000

        # Si el porcentaje asignado es menor al 5%, también penalizamos para evitar "migajas"
        if 0 < pct < 5:
            error_total += 100000

    # Penalizaciones de riesgo y distribución
    if salario < 3000000 and pct_riesgosos > 40:
        error_total += (pct_riesgosos - 40) * 20000

    for cat, pct_meta in objetivo.items():
        error_total += abs(individuo.get(cat, {}).get("porcentaje", 0) - pct_meta) * 800

    for cat, datos in individuo.items():
        if datos["porcentaje"] > 50:
            error_total += (datos["porcentaje"] - 50) * 15000

    # A mayor error, la aptitud tiende a cero de forma drástica
    aptitud = (rendimiento_total + 1) / (1 + error_total)

    stats = {
        "rendimiento_anual_cop": round(rendimiento_total),
        "pct_riesgosos": round(pct_riesgosos, 1),
        "error_total": round(error_total, 2),
        "tasa_promedio": round((rendimiento_total / ahorro) * 100, 2) if ahorro > 0 else 0
    }
    return aptitud, stats

def seleccion_torneo(poblacion, perfil, torneo_size=3):
    if random.random() < 0.05:
        return copy.deepcopy(random.choice(poblacion))
    torneo = random.sample(poblacion, torneo_size)
    torneo.sort(key=lambda ind: evaluar_aptitud(ind, perfil)[0], reverse=True)
    return copy.deepcopy(torneo[0])

def cruzar(padre1, padre2):
    hijo = {}
    categorias = list(padre1.keys())
    for cat in categorias:
        hijo[cat] = copy.deepcopy(padre1[cat] if random.random() < 0.5 else padre2[cat])
    for cat in categorias:
        if random.random() < 0.6:
            p1 = padre1[cat]["porcentaje"]
            p2 = padre2[cat]["porcentaje"]
            mezcla = 0.5 * p1 + 0.5 * p2 + random.uniform(-2, 2)
            hijo[cat]["porcentaje"] = max(0.1, min(99.9, round(mezcla, 1)))
    _normalizar_porcentajes(hijo)
    return hijo

def mutar(individuo, catalogo_seguro):
    if random.random() < TASA_MUTACION:
        categorias = list(individuo.keys())
        tipo = random.choice(["producto", "porcentaje"])
        if tipo == "producto":
            cat_elegida = random.choice(categorias)
            if cat_elegida in catalogo_seguro:
                individuo[cat_elegida]["producto"] = random.choice(catalogo_seguro[cat_elegida])
        else:
            cambios = random.sample(categorias, k=max(1, len(categorias) // 3))
            for cat in cambios:
                individuo[cat]["porcentaje"] = max(0.1, min(99.9, individuo[cat]["porcentaje"] + random.uniform(-3, 3)))
            _normalizar_porcentajes(individuo)
    return individuo

def ejecutar_ag(perfil, catalogo_seguro):
    poblacion = [crear_individuo(perfil, catalogo_seguro) for _ in range(TAMANO_POBLACION)]
    poblacion_evaluada = [(ind, evaluar_aptitud(ind, perfil)) for ind in poblacion]
    poblacion_evaluada.sort(key=lambda x: x[1][0], reverse=True)
    mejor_historico, (mejor_aptitud_historica, mejores_stats) = poblacion_evaluada[0]
    mejor_historico = copy.deepcopy(mejor_historico)

    for generacion in range(GENERACIONES):
        poblacion_evaluada = [(ind, evaluar_aptitud(ind, perfil)) for ind in poblacion]
        poblacion_evaluada.sort(key=lambda x: x[1][0], reverse=True)

        elites = [copy.deepcopy(entry[0]) for entry in poblacion_evaluada[:2]]
        nueva_poblacion = list(elites)

        mejor_actual, (aptitud_actual, stats_actual) = poblacion_evaluada[0]
        if aptitud_actual > mejor_aptitud_historica:
            mejor_historico = copy.deepcopy(mejor_actual)
            mejor_aptitud_historica = aptitud_actual
            mejores_stats = stats_actual

        while len(nueva_poblacion) < TAMANO_POBLACION:
            padre1 = seleccion_torneo(poblacion, perfil)
            padre2 = seleccion_torneo(poblacion, perfil)
            nueva_poblacion.append(mutar(cruzar(padre1, padre2), catalogo_seguro))

        poblacion = nueva_poblacion

    return mejor_historico, mejores_stats, mejor_aptitud_historica

# ==================================================
# ORQUESTADOR PRINCIPAL MAPEADO PARA REACT
# ==================================================
def optimizar_perfil(perfil_usuario):
    """Mapea los datos de salida exactamente como el Frontend los requiere."""
    perfil, catalogo_seguro = preparar_entorno_evolutivo(perfil_usuario)
    mejor_portafolio, stats, aptitud = ejecutar_ag(perfil, catalogo_seguro)

    ahorro = perfil["ahorro_inversion"]
    rendimiento_total = 0.0
    portafolio = []

    for cat, datos in mejor_portafolio.items():
        pct = datos["porcentaje"]
        if pct < 1.0: continue # Ignoramos remanentes insignificantes
        
        producto = datos["producto"]
        monto_mensual = round((pct / 100) * ahorro)
        tasa = producto["tasa"] # Por ejemplo 0.12 para 12%
        rendimiento = monto_mensual * tasa
        rendimiento_total += rendimiento
        
        # 🚨 AQUÍ EL MAPEO CRUCIAL PARA LA UI DE REACT:
        # Tu frontend busca propiedades directas dentro de cada tarjeta del portafolio.
        portafolio.append({
            "categoria": cat.upper(),
            "producto": producto["nombre"],           # Mapeo directo de 'nombre'
            "nombre": producto["nombre"],             # Duplicamos por si acaso
            "porcentaje": pct,
            "monto_mensual": monto_mensual,
            "tasa": tasa,                             # Enviamos la tasa real decimal (Vite suele multiplicarla por 100 en la UI)
            "riesgo": producto["riesgo"].capitalize(),
            "liquidez": producto["liquidez"],
            "minimo": producto["minimo"],
            "rendimiento_anual_estimado": round(rendimiento * 12)
        })

    capital_12 = ahorro * 12
    valor_proyectado = capital_12 + (rendimiento_total * 12)
    fondo_emergencia = perfil["necesidades"] * perfil["fondo_emergencia_meses"]

    return {
        "perfil": perfil,
        "portafolio": portafolio,
        "stats": stats,
        "aptitud": round(aptitud, 4),
        "valor_proyectado": round(valor_proyectado),
        "fondo_emergencia": fondo_emergencia,
    }