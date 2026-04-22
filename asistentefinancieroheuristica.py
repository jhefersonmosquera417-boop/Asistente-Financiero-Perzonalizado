import json

# Cargar catálogo de inversiones desde el archivo JSONL
catalogo_inversiones = {}
with open("dataset_catalogo_inversiones.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line.strip())
        categoria = item.pop('categoria')
        if categoria not in catalogo_inversiones:
            catalogo_inversiones[categoria] = []
        catalogo_inversiones[categoria].append(item)

PORTAFOLIO_GENERADO = {
  "distribucion_mensual": {
    "necesidades": 875000,
    "deseos": 525000,
    "ahorro_inversion": 350000
  },
  "estrategia": "Priorizar la compra de una casa",
  "portafolio": {
    "inversiones": [
      {
        "tipo": "casa",
        "valor": 300000
      }
    ]
  },
  "ahorro_detallado": {
    "deuda": 105000,
    "fondo_emergencia": 52500,
    "ahorro_vivienda": 140000,
    "inversion": 52500
  },
  "portafolio_inversion": {
    "cdt": 21000,
    "fondos_inversion": 15750,
    "acciones": 10500,
    "bonos": 0,
    "criptomonedas": 0,
    "oro": 5250
  },
  "proyeccion_12_meses": {
    "ahorro_total": 4200000
  },
  "advertencia": "Simulación educativa. No es asesoría financiera profesional."
}

# ==========================================================
# 3. NORMALIZACIÓN SEMÁNTICA DE RIESGO
# ==========================================================

def interpretar_riesgo(texto_estrategia):
    texto = texto_estrategia.lower()

    if "conservador" in texto:
        return "bajo"
    elif "moderado" in texto:
        return "medio"
    elif "agresivo" in texto or "alto" in texto:
        return "alto"
    else:
        return "medio"

# ==========================================================
# 4. FILTRO POR RIESGO
# ==========================================================

def filtrar_por_riesgo(catalogo, riesgo_maximo):
    niveles = {"bajo": 1, "medio": 2, "alto": 3}

    if riesgo_maximo not in niveles:
        print(f"Perfil de riesgo desconocido: {riesgo_maximo}. Usando 'medio'.")
        riesgo_maximo = "medio"

    catalogo_filtrado = {}

    for categoria, productos in catalogo.items():
        catalogo_filtrado[categoria] = [
            p for p in productos
            if niveles[p["riesgo"]] <= niveles[riesgo_maximo]
        ]

    return catalogo_filtrado

# ==========================================================
# 5. HEURÍSTICA VORAZ
# ==========================================================

def generar_portafolio_voraz(catalogo_filtrado, presupuesto):
    inversiones = []
    dinero_restante = presupuesto

    todos = []
    for productos in catalogo_filtrado.values():
        todos.extend(productos)

    todos = sorted(todos, key=lambda x: x["tasa"], reverse=True)

    for producto in todos:
        if dinero_restante >= producto["minimo"]:
            inversiones.append(producto)
            dinero_restante -= producto["minimo"]

    return inversiones, dinero_restante

# ==========================================================
# 6. MAIN
# ==========================================================

def main():
    print("====================================================")
    print("MOTOR HEURÍSTICO DE OPTIMIZACIÓN FINANCIERA")
    print("====================================================\n")

    ahorro = PORTAFOLIO_GENERADO["distribucion_mensual"]["ahorro_inversion"]

    riesgo = interpretar_riesgo(PORTAFOLIO_GENERADO["estrategia"])
    print(f"Perfil detectado desde Llama: {riesgo}\n")

    print("1. Filtrando productos según perfil de riesgo...")
    catalogo_filtrado = filtrar_por_riesgo(catalogo_inversiones, riesgo)

    print("2. Ejecutando heurística voraz para asignación de capital...\n")
    inversiones, restante = generar_portafolio_voraz(catalogo_filtrado, ahorro)

    if inversiones:
        print("PORTAFOLIO SELECCIONADO:")
        for inv in inversiones:
            print(f"{inv['id']} | tasa: {inv['tasa']*100:.2f}% | mínimo: {inv['minimo']}")

        print("\nRESUMEN")
        print(f"Capital invertido: {ahorro - restante}")
        print(f"Capital restante: {restante}")
    else:
        print("No se pudo generar portafolio con las restricciones.")

    # Guardar resultados en archivo JSON
    resultados = {
        "perfil_riesgo": riesgo,
        "ahorro_disponible": ahorro,
        "portafolio_seleccionado": [
            {
                "id": inv["id"],
                "tipo": next((cat for cat, prods in catalogo_inversiones.items() if any(p["id"] == inv["id"] for p in prods)), "desconocido"),
                "tasa": inv["tasa"],
                "minimo": inv["minimo"]
            } for inv in inversiones
        ],
        "capital_invertido": ahorro - restante,
        "capital_restante": restante
    }

    with open("portafolio_heuristico.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)

    print("\nResultados guardados en 'portafolio_heuristico.json'.")

if __name__ == "__main__":
    main()