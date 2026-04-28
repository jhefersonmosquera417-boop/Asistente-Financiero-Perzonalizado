import json

# ==========================================================
# 1. CONFIGURACIÓN Y REGLAS DE NEGOCIO
# ==========================================================
SMMLV_2026 = 1750905  # Salario mínimo proyectado en tu proyecto

# Distribución técnica profesional por perfil
DISTRIBUCIONES = {
    "bajo":  {"cdt": 0.60, "fondos_inversion": 0.30, "oro": 0.10},
    "medio": {"cdt": 0.60, "fondos_inversion": 0.30, "acciones": 0.10},
    "alto":  {"acciones": 0.50, "criptomonedas": 0.30, "fondos_inversion": 0.20}
}

# ==========================================================
# 2. FUNCIONES DE APOYO
# ==========================================================
def normalizar_categoria(cat):
    mapa = {
        "fondos": "fondos_inversion",
        "criptomoneda": "criptomonedas",
        "bonos": "bonos"
    }
    return mapa.get(cat, cat)

def interpretar_riesgo(estrategia):
    est = estrategia.lower()
    if "alto" in est: return "alto"
    if "medio" in est: return "medio"
    return "bajo"

def filtrar_por_riesgo(catalogo, riesgo):
    filtrado = {}
    niveles = {"bajo": 1, "medio": 2, "alto": 3}
    riesgo_usuario = niveles.get(riesgo, 1)
    
    for cat, productos in catalogo.items():
        # Solo productos cuyo riesgo sea igual o menor al del usuario
        prods_validos = [p for p in productos if niveles.get(p['riesgo'], 1) <= riesgo_usuario]
        if prods_validos:
            filtrado[cat] = prods_validos
    return filtrado

# ==========================================================
# 3. CARGAR CATÁLOGO DE DATOS
# ==========================================================
catalogo_inversiones = {}
try:
    with open("dataset_catalogo_inversiones.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line.strip())
            categoria = normalizar_categoria(item.pop('categoria'))
            if categoria not in catalogo_inversiones:
                catalogo_inversiones[categoria] = []
            catalogo_inversiones[categoria].append(item)
except FileNotFoundError:
    print("Error: No se encontró el archivo 'dataset_catalogo_inversiones.jsonl'")

# ==========================================================
# 4. DATOS DE ENTRADA (SIMULACIÓN)
# ==========================================================
PORTAFOLIO_GENERADO = {
  "distribucion_mensual": {
    "salario": 1750000,
    "necesidades": 875000,
    "deseos": 525000,
    "ahorro_inversion": 350000
  },
  "estrategia": "Perfil Medio detectado"
}

# ==========================================================
# 5. MOTOR DE ASIGNACIÓN INTELIGENTE
# ==========================================================
def generar_portafolio_mejorado(catalogo, ahorro, riesgo, salario):
    portafolio = {}
    restante = ahorro
    
    # Obtener pesos del perfil
    pesos = DISTRIBUCIONES.get(riesgo, DISTRIBUCIONES["bajo"]).copy()
    
    # RESTRICCIÓN DE SEGURIDAD (ESCUDO SMMLV)
    # Si gana menos de 2 mínimos, el riesgo alto se limita al 10%
    if salario < (2 * SMMLV_2026):
        activos_volatiles = ["acciones", "criptomonedas"]
        peso_volatil_total = sum(pesos.get(a, 0) for a in activos_volatiles)
        
        if peso_volatil_total > 0.10:
            exceso = peso_volatil_total - 0.10
            for a in activos_volatiles:
                if a in pesos:
                    # Reducir proporcionalmente al 10% total
                    pesos[a] = (pesos[a] / peso_volatil_total) * 0.10
            # El excedente de riesgo se mueve al activo más seguro (CDT)
            pesos["cdt"] = pesos.get("cdt", 0) + exceso

    # Asignación de capital por porcentajes
    for cat, porcentaje in pesos.items():
        if porcentaje > 0 and cat in catalogo:
            monto = ahorro * porcentaje
            portafolio[cat] = round(monto)
            restante -= monto

    return portafolio, restante

# ==========================================================
# 6. EJECUCIÓN PRINCIPAL (MAIN)
# ==========================================================
def main():
    print("==== MOTOR FINANCIERO INTELIGENTE (VERSIÓN 100/100) ====\n")

    datos = PORTAFOLIO_GENERADO["distribucion_mensual"]
    ahorro = datos["ahorro_inversion"]
    salario = datos["salario"]
    # Nota: Asegúrate de tener definida la variable SMMLV_2026 o cámbiala por el número 1750905
    limite_smmlv = 1750905 

    riesgo = interpretar_riesgo(PORTAFOLIO_GENERADO["estrategia"])

    # --- BLOQUE DE PROCESAMIENTO ---
    catalogo_filtrado = filtrar_por_riesgo(catalogo_inversiones, riesgo)
    
    print(f"Perfil detectado: {riesgo}")
    print("DEBUG PRODUCTOS DISPONIBLES:")
    for cat, prods in catalogo_filtrado.items():
        print(f" - {cat}: {len(prods)} opciones encontradas")
    
    print(f"\nSalario base: ${salario:,} COP")
    if salario < (2 * limite_smmlv):
        print("ESTADO: Aplicando restricción de seguridad por ingresos < 2 SMMLV.")
    
    print("\nGenerando portafolio estratégico...")

    portafolio, restante = generar_portafolio_mejorado(
        catalogo_filtrado, 
        ahorro, 
        riesgo, 
        salario
    )

    # --- IMPRESIÓN DE TABLA EN TERMINAL ---
    print("-" * 45)
    print(f"{'CATEGORÍA':<20} | {'MONTO SUGERIDO':<15}")
    print("-" * 45)
    for cat, monto in portafolio.items():
        if monto > 0:
            print(f"{cat.upper():<20} | ${monto:>14,}")
    
    print("-" * 45)
    invertido_total = ahorro - restante
    print(f"{'TOTAL INVERTIDO':<20} | ${int(invertido_total):>14,}")
    print(f"{'CAPITAL EN RESERVA':<20} | ${int(restante):>14,}")
    print("-" * 45)

    # --- ACTUALIZACIÓN DEL DICCIONARIO PARA EL JSON ---
    PORTAFOLIO_GENERADO["portafolio_inversion"] = portafolio
    
    # AGREGAR EL RESUMEN AL DICCIONARIO (Esto es lo que pediste ver en el JSON)
    PORTAFOLIO_GENERADO["resumen"] = {
        "invertido": float(invertido_total),
        "restante": float(restante)
    }

    # --- BLOQUE DE RESUMEN FINAL EN PANTALLA ---
    print("\n" + "="*30)
    print("           RESUMEN")
    print("="*30)
    print(f"Invertido: {float(invertido_total):,}")
    print(f"Restante:  {float(restante):,}")
    print("="*30 + "\n")

    # --- GUARDAR ARCHIVO ---
    with open("portafolio_heuristico.json", "w", encoding="utf-8") as f:
        json.dump(PORTAFOLIO_GENERADO, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Archivo 'portafolio_heuristico.json' actualizado con éxito.")



if __name__ == "__main__":
    main()