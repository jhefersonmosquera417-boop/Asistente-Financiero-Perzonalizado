import json

# ==========================================================
# 1. NORMALIZACIÓN DE CATEGORÍAS
# ==========================================================

def normalizar_categoria(cat):
    mapa = {
        "fondos": "fondos_inversion",
        "criptomoneda": "criptomonedas"
    }
    return mapa.get(cat, cat)

# ==========================================================
# 2. CARGAR CATÁLOGO
# ==========================================================

catalogo_inversiones = {}

with open("dataset_catalogo_inversiones.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line.strip())
        categoria = normalizar_categoria(item.pop('categoria'))

        if categoria not in catalogo_inversiones:
            catalogo_inversiones[categoria] = []

        catalogo_inversiones[categoria].append(item)

# ==========================================================
# 3. PORTAFOLIO BASE
# ==========================================================

PORTAFOLIO_GENERADO = {
  "distribucion_mensual": {
    "necesidades": 875000,
    "deseos": 525000,
    "ahorro_inversion": 350000
  },
  "estrategia": "Priorizar la compra de una casa",
  "portafolio": {
    "inversiones": [
      {"tipo": "casa", "valor": 300000}
    ]
  },
  "ahorro_detallado": {
    "deuda": 105000,
    "fondo_emergencia": 52500,
    "ahorro_vivienda": 140000,
    "inversion": 52500
  },
  "portafolio_inversion": {},
  "proyeccion_12_meses": {
    "ahorro_total": 4200000
  },
  "advertencia": "Simulación educativa. No es asesoría financiera profesional."
}

# ==========================================================
# 4. INTERPRETAR RIESGO
# ==========================================================

def interpretar_riesgo(texto):
    texto = texto.lower()

    if "conservador" in texto:
        return "bajo"
    elif "moderado" in texto:
        return "medio"
    elif "agresivo" in texto or "alto" in texto:
        return "alto"
    return "medio"

# ==========================================================
# 5. FILTRO POR RIESGO
# ==========================================================

def filtrar_por_riesgo(catalogo, riesgo):
    niveles = {"bajo": 1, "medio": 2, "alto": 3}

    return {
        cat: [p for p in prods if niveles[p["riesgo"]] <= niveles[riesgo]]
        for cat, prods in catalogo.items()
    }

# ==========================================================
# 6. HEURÍSTICA FINAL (ADAPTATIVA)
# ==========================================================

def generar_portafolio_mejorado(catalogo, presupuesto, riesgo):

    distribucion = {
        "bajo": {"cdt": 0.5, "fondos_inversion": 0.3, "bonos": 0.2},
        "medio": {"cdt": 0.3, "fondos_inversion": 0.3, "acciones": 0.2, "bonos": 0.1, "oro": 0.1},
        "alto": {"acciones": 0.4, "fondos_inversion": 0.3, "criptomonedas": 0.2, "oro": 0.1}
    }

    plan = distribucion[riesgo]

    # 🔥 1. SOLO CATEGORÍAS DISPONIBLES
    disponibles = {
        cat: peso for cat, peso in plan.items()
        if cat in catalogo and len(catalogo[cat]) > 0
    }

    # 🔥 2. NORMALIZAR PESOS
    total = sum(disponibles.values())
    disponibles = {cat: peso / total for cat, peso in disponibles.items()}

    portafolio = {
        "cdt": 0,
        "fondos_inversion": 0,
        "acciones": 0,
        "bonos": 0,
        "criptomonedas": 0,
        "oro": 0
    }

    restante = presupuesto

    # 🔥 3. ASIGNACIÓN INTELIGENTE
    for categoria, porcentaje in disponibles.items():
        capital = presupuesto * porcentaje
        productos = sorted(catalogo[categoria], key=lambda x: x["tasa"], reverse=True)

        for p in productos:
            if capital >= p["minimo"]:
                portafolio[categoria] += p["minimo"]
                capital -= p["minimo"]
                restante -= p["minimo"]

        # usar sobrante
        if capital > 0 and productos:
            portafolio[categoria] += capital
            restante -= capital

    return portafolio, restante

# ==========================================================
# 7. MAIN
# ==========================================================

def main():

    print("==== MOTOR FINANCIERO INTELIGENTE ====\n")

    ahorro = PORTAFOLIO_GENERADO["distribucion_mensual"]["ahorro_inversion"]
    riesgo = interpretar_riesgo(PORTAFOLIO_GENERADO["estrategia"])

    print(f"Perfil detectado: {riesgo}\n")

    catalogo_filtrado = filtrar_por_riesgo(catalogo_inversiones, riesgo)

    # DEBUG
    print("DEBUG PRODUCTOS:")
    for cat, prods in catalogo_filtrado.items():
        print(f"{cat}: {len(prods)} productos")

    print("\nGenerando portafolio...\n")

    portafolio, restante = generar_portafolio_mejorado(
        catalogo_filtrado,
        ahorro,
        riesgo
    )

    PORTAFOLIO_GENERADO["portafolio_inversion"] = portafolio

    print("PORTAFOLIO FINAL:")
    for k, v in portafolio.items():
        print(f"{k}: {int(v)}")

    print("\nRESUMEN")
    print(f"Invertido: {ahorro - restante}")
    print(f"Restante: {int(restante)}")

    with open("portafolio_final.json", "w", encoding="utf-8") as f:
        json.dump(PORTAFOLIO_GENERADO, f, indent=4, ensure_ascii=False)

    print("\nArchivo guardado: portafolio_final.json")

# ==========================================================
# EJECUCIÓN
# ==========================================================

if __name__ == "__main__":
    main()