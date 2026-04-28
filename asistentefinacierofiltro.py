import ollama
import json
import os

MODELO = "llama3.2"
ARCHIVO_DATOS = "dataset_finanzas_colombia.jsonl"

# ======================================================
# TASAS POR PERFIL DE RIESGO (mercado colombiano 2026)
# ======================================================
TASAS = {
    "bajo":  {"cdt": 0.112, "fondos_inversion": 0.092, "oro": 0.090},
    "medio": {"cdt": 0.118, "fondos_inversion": 0.110, "acciones": 0.080},
    "alto":  {"acciones": 0.140, "criptomonedas": 0.150, "fondos_inversion": 0.120},
}

# Distribución del portafolio por perfil de riesgo
DISTRIBUCION_PORTAFOLIO = {
    "bajo":  {"cdt": 0.60, "fondos_inversion": 0.30, "oro": 0.10},
    "medio": {"cdt": 0.60, "fondos_inversion": 0.30, "acciones": 0.10},
    "alto":  {"acciones": 0.50, "criptomonedas": 0.30, "fondos_inversion": 0.20},
}

def cargar_contexto_desde_archivo():
    """Carga ejemplos del dataset como contexto para el LLM (solo para recomendaciones textuales)."""
    mensajes = []
    prompt = """
Eres un planificador financiero educativo para Colombia.
Tu única función es generar una recomendación textual breve (máximo 3 líneas)
sobre la estrategia financiera según el perfil del usuario.
NO calcules ningún número. Los cálculos ya están hechos por el sistema.
Solo responde con el texto de recomendación, sin JSON, sin listas, sin títulos.
"""
    mensajes.append({"role": "system", "content": prompt})

    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            # Solo cargar 20 ejemplos para no sobrecargar el contexto
            for linea in lineas[:20]:
                try:
                    d = json.loads(linea)
                    mensajes.append({"role": "user",      "content": d["input"]})
                    mensajes.append({"role": "assistant", "content": d["output"]})
                except:
                    continue
    return mensajes


def calcular_proyeccion_interes_compuesto(aporte_mensual, tasa_anual):
    """
    Fórmula correcta de valor futuro con aportes mensuales periódicos.
    VF = A × [(1 + r)^n - 1] / r
    donde r = tasa mensual equivalente, n = 12 meses
    """
    tasa_mensual = (1 + tasa_anual) ** (1 / 12) - 1
    valor_futuro = aporte_mensual * ((1 + tasa_mensual) ** 12 - 1) / tasa_mensual
    rendimiento  = valor_futuro - (aporte_mensual * 12)
    return round(valor_futuro), round(rendimiento)


def calcular_plan(salario, riesgo, deudas, objetivo):
    """
    Calcula TODO el plan financiero en Python puro.
    No depende del LLM para ningún número.
    """
    riesgo_key = riesgo.lower()

    # ── 1. REGLA 50/30/20 ─────────────────────────────────────────────
    necesidades = round(salario * 0.50)
    deseos      = round(salario * 0.30)
    ahorro      = salario - necesidades - deseos   # exactamente el 20%

    # ── 2. FONDO DE EMERGENCIA ────────────────────────────────────────
    # Correcto: 3 meses de NECESIDADES (no del salario completo)
    meta_fondo_emergencia = necesidades * 3

    # ── 3. DISTRIBUCIÓN DEL AHORRO ────────────────────────────────────
    ahorro_restante = ahorro

    # Deudas (30% del ahorro si hay deudas)
    pago_deuda = round(ahorro * 0.30) if deudas > 0 else 0
    ahorro_restante -= pago_deuda

    # Ahorro vivienda (40% del ahorro si el objetivo es casa)
    tiene_objetivo_vivienda = any(p in objetivo.lower() for p in ["casa", "vivienda", "hogar", "apartamento"])
    ahorro_vivienda = round(ahorro * 0.40) if tiene_objetivo_vivienda else 0
    ahorro_restante -= ahorro_vivienda

    # Del restante: 30% fondo emergencia, 70% inversión
    fondo_emergencia = round(ahorro_restante * 0.30)
    inversion        = ahorro_restante - fondo_emergencia

    # Verificar que todo suma exactamente el ahorro
    suma_check = pago_deuda + ahorro_vivienda + fondo_emergencia + inversion
    # Ajustar diferencia de redondeo en inversión
    inversion += (ahorro - suma_check)

    # ── 4. PORTAFOLIO DE INVERSIÓN ────────────────────────────────────
    distribucion = DISTRIBUCION_PORTAFOLIO.get(riesgo_key, DISTRIBUCION_PORTAFOLIO["medio"])
    tasas        = TASAS.get(riesgo_key, TASAS["medio"])

    portafolio = {
        "cdt":            0,
        "fondos_inversion": 0,
        "acciones":       0,
        "bonos":          0,
        "criptomonedas":  0,
        "oro":            0
    }

    montos_por_instrumento = {}
    asignado = 0
    items = list(distribucion.items())

    for i, (instrumento, pct) in enumerate(items):
        if i < len(items) - 1:
            monto = round(inversion * pct)
        else:
            monto = inversion - asignado   # el último absorbe el redondeo
        portafolio[instrumento] = monto
        montos_por_instrumento[instrumento] = monto
        asignado += monto

    # ── 5. PROYECCIÓN A 12 MESES (interés compuesto) ──────────────────
    capital_total     = ahorro * 12
    rendimiento_total = 0
    proyeccion_por_instrumento = {}

    for instrumento, monto in montos_por_instrumento.items():
        if monto > 0 and instrumento in tasas:
            vf, rend = calcular_proyeccion_interes_compuesto(monto, tasas[instrumento])
            proyeccion_por_instrumento[instrumento] = {
                "aporte_mensual":   monto,
                "capital_12_meses": monto * 12,
                "rendimiento":      rend,
                "valor_futuro":     vf,
                "tasa_anual_ea":    f"{tasas[instrumento]*100:.1f}%"
            }
            rendimiento_total += rend

    valor_futuro_total = capital_total + rendimiento_total

    # ── 6. ARMAR JSON FINAL ───────────────────────────────────────────
    plan = {
        "distribucion_mensual": {
            "salario":         salario,
            "necesidades_50pct": necesidades,
            "deseos_30pct":    deseos,
            "ahorro_20pct":    ahorro
        },
        "fondo_emergencia_meta": meta_fondo_emergencia,
        "ahorro_detallado": {
            "deuda":            pago_deuda,
            "fondo_emergencia": fondo_emergencia,
            "ahorro_vivienda":  ahorro_vivienda,
            "inversion":        inversion,
            "suma_verificacion": pago_deuda + fondo_emergencia + ahorro_vivienda + inversion
        },
        "portafolio_inversion": portafolio,
        "proyeccion_12_meses": {
            "capital_total_aportado":  capital_total,
            "rendimiento_con_interes": rendimiento_total,
            "valor_futuro_total":      valor_futuro_total,
            "detalle_por_instrumento": proyeccion_por_instrumento
        },
        "advertencia": "Simulación educativa. No constituye asesoría financiera legal ni profesional."
    }

    return plan


def obtener_recomendacion_llm(historial, salario, riesgo, objetivo, deudas):
    """Pide al LLM solo la recomendación textual, no los números."""
    try:
        msgs = historial.copy()
        msgs.append({
            "role": "user",
            "content": (
                f"Salario: {salario:,} COP. Riesgo: {riesgo}. "
                f"Objetivo: {objetivo}. Deudas: {deudas:,} COP. "
                f"Dame una recomendación estratégica breve en 2-3 líneas."
            )
        })
        r = ollama.chat(
            model=MODELO,
            messages=msgs,
            options={"temperature": 0.2}
        )
        return r["message"]["content"].strip()
    except:
        return "Recomendación no disponible (modelo offline)."


def main():
    historial = cargar_contexto_desde_archivo()

    print("\n=== MOTOR FINANCIERO INTELIGENTE ===")
    print("Todos los cálculos siguen la regla 50/30/20 exacta.\n")

    while True:
        entrada = input("salario,riesgo,deudas,objetivo:\n> ").strip()

        if entrada.lower() in {"salir", "exit", "quit"}:
            break

        try:
            partes  = entrada.split(",")
            salario = int(partes[0].strip().replace(".", "").replace(",", ""))
            riesgo  = partes[1].strip().capitalize()
            deudas  = int(partes[2].strip())
            objetivo = partes[3].strip().lower() if len(partes) > 3 else "general"
        except Exception as e:
            print(f"  Entrada inválida. Formato: 1750000,medio,0,casa\n")
            continue

        if riesgo.lower() not in ["bajo", "medio", "alto"]:
            print("  Riesgo inválido. Usa: bajo, medio o alto\n")
            continue

        # Calcular plan financiero con Python puro (100% exacto)
        plan = calcular_plan(salario, riesgo, deudas, objetivo)

        # Pedir recomendación textual al LLM (solo texto, sin números)
        recomendacion = obtener_recomendacion_llm(historial, salario, riesgo, objetivo, deudas)
        plan["recomendacion_estrategica"] = recomendacion

        print("\n" + json.dumps(plan, indent=2, ensure_ascii=False))

        # Guardar resultado
        with open("portafolio_final.json", "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        print("\n  Guardado en portafolio_final.json\n")


if __name__ == "__main__":
    main()