import math
from typing import Any, Dict, List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ollama import chat

from asistentefinancieroevolutivo import optimizar_perfil, cargar_catalogo
from asistente_financiero_inteligente import analisis_inteligente as generar_analisis_inteligente

app = FastAPI(title="Asistente Financiero", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL = "llama3.2"
SMMLV = 1_750_905  # SMMLV Colombia 2026

# ── Modelos Pydantic ─────────────────────────────────────────
class ConsultaFinanciera(BaseModel):
    salario: int
    nivel_riesgo: str
    objetivo_financiero: str
    horizonte: str
    fondo_emergencia: bool = True
    endeudamiento: bool = False
    gastos_fijos: int = 0
    deudas: int = 0           # monto mensual de deudas
    ahorro_real: int = 0      # ahorro real enviado desde el frontend

class RespuestaFinanciera(BaseModel):
    salario: int
    gastos_fijos: int
    deudas: int
    nivel_riesgo: str         # ← corregido (antes era "riesgo", el frontend espera "nivel_riesgo")
    horizonte: str
    objetivo_financiero: str
    fondo_emergencia: bool    # ← bool, no viene del resultado interno
    ahorro_inversion: int
    necesidades: int
    deseos: int
    distribucion_objetivo: dict
    portafolio_optimo: list[dict]
    valor_proyectado: int
    fondo_emergencia_valor: int
    recomendacion: str
    mensaje: str
    endeudamiento_activo: bool

# ── Función de recomendación IA ──────────────────────────────
def obtener_recomendacion_ia(
    salario: int,
    nivel_riesgo: str,
    objetivo: str,
    horizonte: str,
    fondo_emergencia: bool,
    deudas_monto: int = 0,
    gastos_fijos: int = 0,
    ahorro_real: int = 0,
) -> str:
    necesidades       = round(salario * 0.50)
    deseos            = round(salario * 0.30)
    ahorro_bruto      = round(salario * 0.20)
    ahorro_disponible = ahorro_real if ahorro_real > 0 else max(ahorro_bruto - deudas_monto, 0)
    ratio_deuda       = round((deudas_monto / salario) * 100, 1) if salario > 0 else 0
    es_bajo_smmlv     = salario < SMMLV
    tiene_deuda       = deudas_monto > 0
    deuda_alta        = ratio_deuda > 30

    # Meta estimada según objetivo
    objetivo_lower = objetivo.lower()
    if 'emergencia'    in objetivo_lower: meta = necesidades * 3
    elif 'vivienda'    in objetivo_lower: meta = salario * 24
    elif 'educaci'     in objetivo_lower: meta = salario * 12
    elif 'jubilaci'    in objetivo_lower: meta = salario * 120
    elif 'viaje'       in objetivo_lower: meta = salario * 3
    elif 'ocio'        in objetivo_lower: meta = salario * 3
    elif 'emprendimiento' in objetivo_lower: meta = salario * 6
    else:                                 meta = necesidades * 3

    meses     = round(meta / ahorro_disponible) if ahorro_disponible > 0 else 999
    anos_meta = round(meses / 12, 1)

    productos = {
        'Bajo':  'CDT 90 días (10.50% EA), Cuenta remunerada (7.50% EA), FIC Conservador (9.20% EA)',
        'Medio': 'CDT 360 días (11.80% EA), FIC Balanceado (11.00% EA), ETF iColcap (8.00% EA)',
        'Alto':  'FIC Renta Variable (14.00% EA), Acciones BVC (12.00% EA), ETF S&P 500 en COP (15.00% EA)',
    }
    productos_perfil = productos.get(nivel_riesgo, productos['Medio'])

    def pedir_seccion(instruccion: str, max_tokens: int = 200) -> str:
        try:
            r = chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": (
                        "Eres un coach financiero colombiano, cálido y motivador. "
                        "Responde SOLO con el texto solicitado, sin títulos, sin markdown, "
                        "sin asteriscos, sin encabezados. Máximo 3 párrafos cortos. "
                        "Usa español colombiano cercano y empático."
                    )},
                    {"role": "user", "content": instruccion},
                ],
                options={"num_predict": max_tokens},
                stream=False,
            )
            return r.get("message", {}).get("content", "").strip()
        except Exception as e:
            return f"No se pudo generar esta sección: {e}"

    # Texto de cada sección
    texto_momento = pedir_seccion(
        f"El cliente tiene salario de {salario} COP, perfil de riesgo {nivel_riesgo}, "
        f"objetivo '{objetivo}' y horizonte {horizonte}. "
        f"Explica en 2 párrafos qué significa su perfil de riesgo {nivel_riesgo} para su tranquilidad mental "
        f"y su momento de vida. Sé empático y motivador."
    )

    texto_radiografia = pedir_seccion(
        f"El cliente gana {salario} COP. Su distribución 50/30/20 es: "
        f"Necesidades {necesidades} COP, Deseos {deseos} COP, Ahorro bruto {ahorro_bruto} COP. "
        f"{'Tiene deudas de ' + str(deudas_monto) + ' COP mensuales, ahorro real: ' + str(ahorro_disponible) + ' COP.' if tiene_deuda else ''} "
        f"Explica en 1 párrafo qué significa cada rubro en su vida cotidiana. No repitas los números."
    )

    texto_estrategia = pedir_seccion(
        f"El cliente tiene perfil {nivel_riesgo} con ahorro disponible de {ahorro_disponible} COP/mes. "
        f"Productos recomendados: {productos_perfil}. "
        f"{'Tiene deudas de ' + str(deudas_monto) + ' COP (' + str(ratio_deuda) + '% del salario). ' if tiene_deuda else ''}"
        f"Explica en 2 párrafos por qué estos productos protegen su dinero en Colombia. Menciona las tasas EA."
    )

    texto_objetivo = pedir_seccion(
        f"El cliente quiere '{objetivo}'. Necesita ahorrar {meta} COP. "
        f"Con {ahorro_disponible} COP/mes tardará {meses} meses ({anos_meta} años). "
        f"Da 3 pasos concretos y accionables. Cierra con frase motivadora corta."
    )

    # Construir respuesta con formato fijo en Python
    lineas = []
    lineas.append("⚠️ Esta es una simulación con fines educativos.")
    lineas.append("")

    if es_bajo_smmlv:
        lineas.append(
            f"🚨 SALARIO_BAJO: Tu salario de {salario:,} COP está por debajo del mínimo vigente "
            f"({SMMLV:,} COP). Es fundamental blindar primero tu fondo de emergencia antes de invertir, "
            f"para no depender de deudas informales ante imprevistos."
        )
        lineas.append("")

    if tiene_deuda:
        nivel_deuda = "alto" if deuda_alta else "moderado"
        estrategia_deuda = (
            "Considera la estrategia avalancha (pagar primero la deuda de mayor tasa) para liberarte más rápido."
            if deuda_alta else
            "Puedes combinar pago de deuda e inversión, pero prioriza reducirla."
        )
        lineas.append(
            f"⚠️ DEUDA: Tienes un endeudamiento {nivel_deuda} del {ratio_deuda}% de tu salario "
            f"({deudas_monto:,} COP/mes). {estrategia_deuda} "
            f"Tu ahorro real disponible para invertir es {ahorro_disponible:,} COP/mes."
        )
        lineas.append("")

    lineas.append("### 👥 Tu Momento Financiero Actual")
    lineas.append(texto_momento)
    lineas.append("")

    lineas.append("### 📊 La Radiografía de tu Dinero")
    lineas.append(texto_radiografia)
    lineas.append(f"* Necesidades: ${necesidades:,} COP (50%)")
    lineas.append(f"* Deseos: ${deseos:,} COP (30%)")
    lineas.append(f"* Ahorro bruto: ${ahorro_bruto:,} COP (20%)")
    if tiene_deuda:
        lineas.append(f"* Deudas mensuales: ${deudas_monto:,} COP")
        lineas.append(f"* Ahorro real disponible: ${ahorro_disponible:,} COP")
    lineas.append("")

    lineas.append("### 🛡️ Tu Estrategia de Inversión y Protección")
    lineas.append(texto_estrategia)
    lineas.append("")

    lineas.append("### 🎯 Cómo Alcanzar tu Objetivo")
    lineas.append(f"* Meta estimada para '{objetivo}': ${meta:,} COP")
    lineas.append(f"* Ahorro mensual disponible: ${ahorro_disponible:,} COP")
    lineas.append(f"* Tiempo estimado: {meses} meses ({anos_meta} años)")
    lineas.append(texto_objetivo)
    lineas.append("")

    return "\n".join(lineas)

# ── Mensaje resumen ──────────────────────────────────────────
def generar_mensaje(resultado: dict) -> str:
    perfil = resultado["perfil"]
    ahorro = perfil["ahorro_inversion"]
    necesidades = perfil["necesidades"]
    deseos = perfil["deseos"]
    emergencia_valor = resultado["fondo_emergencia"]
    objetivo = perfil.get("objetivo_financiero", "mejorar mis finanzas")
    horizonte = perfil.get("horizonte", "plazo medio")

    mensaje = (
        f"Con un salario mensual de {perfil['salario']:,} COP y un nivel de riesgo {perfil['nivel_riesgo']}, "
        f"te recomendamos destinar {necesidades:,} COP a necesidades, {deseos:,} COP a deseos "
        f"y {ahorro:,} COP al ahorro/inversión. "
        f"Tu objetivo es {objetivo} con un horizonte {horizonte}."
    )
    if perfil["fondo_emergencia_meses"] > 0:
        mensaje += (
            f" Además, se sugiere un fondo de emergencia equivalente a "
            f"{perfil['fondo_emergencia_meses']} meses de necesidades: {emergencia_valor:,} COP."
        )
    else:
        mensaje += " Has indicado que no deseas priorizar un fondo de emergencia en este momento."

    mensaje += (
        f"\n\nEl portafolio óptimo sugerido combina productos diversificados para equilibrar "
        f"rentabilidad y riesgo. Se espera que el ahorro proyectado después de un año sea "
        f"aproximadamente {resultado['valor_proyectado']:,} COP."
    )
    return mensaje

# ── Endpoints ────────────────────────────────────────────────
@app.get("/")
def root():
    return {"mensaje": "Asistente Financiero API activa"}

@app.post("/analizar", response_model=RespuestaFinanciera)
def analizar_finanzas(consulta: ConsultaFinanciera):
    try:
        salario = consulta.salario
        riesgo  = consulta.nivel_riesgo.capitalize()

        if salario <= 0:
            raise HTTPException(status_code=400, detail="Salario debe ser mayor a 0")
        if riesgo not in ["Bajo", "Medio", "Alto"]:
            raise HTTPException(status_code=400, detail="Riesgo debe ser: Bajo, Medio o Alto")

        perfil_input = {
            "salario":              salario,
            "nivel_riesgo":         riesgo,
            "objetivo_financiero":  consulta.objetivo_financiero.strip(),
            "horizonte":            consulta.horizonte.strip(),
            "fondo_emergencia":     consulta.fondo_emergencia,
        }

        resultado = optimizar_perfil(perfil_input)

        recomendacion = obtener_recomendacion_ia(
            salario          = salario,
            nivel_riesgo     = riesgo,
            objetivo         = perfil_input["objetivo_financiero"],
            horizonte        = perfil_input["horizonte"],
            fondo_emergencia = perfil_input["fondo_emergencia"],
            deudas_monto     = consulta.deudas,
            gastos_fijos     = consulta.gastos_fijos,
            ahorro_real      = consulta.ahorro_real,
        )

        return RespuestaFinanciera(
            salario              = salario,
            gastos_fijos         = consulta.gastos_fijos,
            deudas               = consulta.deudas,
            nivel_riesgo         = riesgo,              # ← viene del formulario, siempre correcto
            horizonte            = perfil_input["horizonte"],
            objetivo_financiero  = perfil_input["objetivo_financiero"],
            fondo_emergencia     = consulta.fondo_emergencia,  # ← viene del formulario
            ahorro_inversion     = resultado["perfil"]["ahorro_inversion"],
            necesidades          = resultado["perfil"]["necesidades"],
            deseos               = resultado["perfil"]["deseos"],
            distribucion_objetivo= resultado["perfil"]["distribucion_objetivo"],
            portafolio_optimo    = resultado["portafolio"],
            valor_proyectado     = resultado["valor_proyectado"],
            fondo_emergencia_valor = resultado["fondo_emergencia"],
            recomendacion        = recomendacion,
            mensaje              = generar_mensaje(resultado),
            endeudamiento_activo = consulta.endeudamiento,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/catalogo")
def obtener_catalogo_inversiones():
    try:
        catalogo = cargar_catalogo()
        if not catalogo:
            return {"mensaje": "Catálogo no disponible"}
        return {"inversiones": catalogo}
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health_check():
    try:
        chat(model=MODEL, messages=[{"role": "user", "content": "Hola"}], stream=False)
        return {"status": "OK", "modelo": MODEL}
    except Exception as e:
        return {"status": "ERROR", "detalle": str(e)}

@app.post("/analisis-inteligente")
def analisis_inteligente_route(payload: dict):
    try:
        resultado = generar_analisis_inteligente(payload)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)