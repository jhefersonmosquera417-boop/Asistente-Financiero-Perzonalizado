from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import random
import re
from ollama import chat

# =============== IMPORTAR DEL SCRIPT EVOLUTIVO ===============
from asistentefinancieroevolutivo import optimizar_perfil, cargar_catalogo
from asistente_financiero_inteligente import analisis_inteligente as generar_analisis_inteligente

# =============== CONFIGURACIÓN ===============
app = FastAPI(title="Asistente Financiero", version="1.0")

# CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL = "llama3.2"

SYSTEM = """
Actúa como un Asistente de Planificación Financiera Educativo especializado en el mercado colombiano.

OBJETIVO:
Procesar el salario mensual y nivel de riesgo del usuario para proponer una estructura
de ahorro e inversión basada en la regla 50/30/20.

PERSONALIDAD:
- Español neutro colombiano.
- Profesional, claro y educativo.
- Lenguaje sencillo para personas sin educación financiera.

RESTRICCIONES:
1. Usa EXCLUSIVAMENTE los números del mensaje del usuario.
2. Siempre incluye: "⚠️ Esta es una simulación con fines educativos."
3. Si salario < 1 SMMLV (1.423.500 COP): Prioriza fondo de emergencia.

REGLAS FINANCIERAS (Colombia 2025):
- SMMLV 2025: 1.423.500 COP
- Regla 50/30/20: 50% Necesidades | 30% Deseos | 20% Ahorro/Inversión
- Fondo de emergencia: 3 meses de Necesidades

PRODUCTOS POR PERFIL:
Riesgo Bajo:
  - CDT 90 días: 10.50% EA
  - Cuenta remunerada: 7.50% EA
  - FIC Conservador: 9.20% EA

Riesgo Medio:
  - CDT 360 días: 11.80% EA
  - FIC Balanceado: 11.00% EA
  - ETF iColcap: 8.00% EA

Riesgo Alto:
  - FIC Renta Variable: 14.00% EA
  - Acciones BVC: 12.00% EA
  - ETF S&P 500 en COP: 15.00% EA
"""

# =============== MODELOS PYDANTIC ===============
class ConsultaFinanciera(BaseModel):
    salario: int
    nivel_riesgo: str  # Bajo, Medio, Alto
    objetivo_financiero: str
    horizonte: str
    fondo_emergencia: bool = True

class RespuestaFinanciera(BaseModel):
    salario: int
    nivel_riesgo: str
    objetivo_financiero: str
    horizonte: str
    fondo_emergencia: bool
    ahorro_inversion: int
    necesidades: int
    deseos: int
    distribucion_objetivo: dict
    portafolio_optimo: list[dict]
    valor_proyectado: int
    fondo_emergencia_valor: int
    recomendacion: str
    mensaje: str

# =============== FUNCIONES AUXILIARES ===============
def obtener_recomendacion_ia(salario: int, nivel_riesgo: str, objetivo: str, horizonte: str, fondo_emergencia: bool) -> str:
    """Consulta Ollama para obtener recomendación personalizada"""
    try:
        prompt = f"""
        Cliente con salario: ${salario:,} COP
        Nivel de riesgo: {nivel_riesgo}
        Objetivo financiero: {objetivo}
        Horizonte: {horizonte}
        Fondo de emergencia incluido: {'sí' if fondo_emergencia else 'no'}
        
        Proporciona una recomendación de inversión en 2-3 párrafos basada en esta información.
        """
        
        response = chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        return response.get("message", {}).get("content", "No se pudo generar recomendación")
    except Exception as e:
        return f"Error al generar recomendación: {str(e)}"


def generar_mensaje(resultado: dict) -> str:
    perfil = resultado["perfil"]
    ahorro = perfil["ahorro_inversion"]
    necesidades = perfil["necesidades"]
    deseos = perfil["deseos"]
    emergencia_valor = resultado["fondo_emergencia"]
    objetivo = perfil.get("objetivo_financiero", "mejorar mis finanzas")
    horizonte = perfil.get("horizonte", "plazo medio")
    mensaje = (
        f"Con un salario mensual de ${perfil['salario']:,} COP y un nivel de riesgo {perfil['nivel_riesgo']}, "
        f"te recomendamos destinar {necesidades:,} COP a necesidades, {deseos:,} COP a deseos y {ahorro:,} COP al ahorro/inversión. "
        f"Tu objetivo es {objetivo} con un horizonte {horizonte}."
    )

    if perfil["fondo_emergencia_meses"] > 0:
        mensaje += (
            f" Además, se sugiere un fondo de emergencia equivalente a {perfil['fondo_emergencia_meses']} meses "
            f"de necesidades: {emergencia_valor:,} COP."
        )
    else:
        mensaje += " Has indicado que no deseas priorizar un fondo de emergencia en este momento."

    mensaje += "\n\nEl portafolio óptimo sugerido combina productos diversificados para equilibrar rentabilidad y riesgo." \
               f" Se espera que el ahorro proyectado después de un año sea aproximadamente {resultado['valor_proyectado']:,} COP."
    return mensaje

# =============== ENDPOINTS ===============
@app.get("/")
def root():
    """Health check"""
    return {"mensaje": "Asistente Financiero API activa"}

@app.post("/analizar", response_model=RespuestaFinanciera)
def analizar_finanzas(consulta: ConsultaFinanciera):
    """Analiza perfil financiero usando lógica evolutiva"""
    try:
        salario = consulta.salario
        riesgo = consulta.nivel_riesgo.capitalize()
        
        # Validaciones
        if salario <= 0:
            raise HTTPException(status_code=400, detail="Salario debe ser mayor a 0")
        if riesgo not in ["Bajo", "Medio", "Alto"]:
            raise HTTPException(status_code=400, detail="Riesgo debe ser: Bajo, Medio o Alto")
        
        perfil_input = {
            "salario": salario,
            "nivel_riesgo": riesgo,
            "objetivo_financiero": consulta.objetivo_financiero.strip(),
            "horizonte": consulta.horizonte.strip(),
            "fondo_emergencia": consulta.fondo_emergencia,
        }

        # Obtener análisis con el algoritmo evolutivo
        resultado = optimizar_perfil(perfil_input)
        
        # Obtener recomendación de IA
        recomendacion = obtener_recomendacion_ia(
            salario,
            riesgo,
            perfil_input["objetivo_financiero"],
            perfil_input["horizonte"],
            perfil_input["fondo_emergencia"]
        )
        
        return RespuestaFinanciera(
            salario=resultado["perfil"]["salario"],
            nivel_riesgo=resultado["perfil"]["nivel_riesgo"],
            objetivo_financiero=resultado["perfil"].get("objetivo_financiero", perfil_input["objetivo_financiero"]),
            horizonte=resultado["perfil"].get("horizonte", perfil_input["horizonte"]),
            fondo_emergencia=resultado["perfil"].get("fondo_emergencia", perfil_input["fondo_emergencia"]),
            ahorro_inversion=resultado["perfil"]["ahorro_inversion"],
            necesidades=resultado["perfil"]["necesidades"],
            deseos=resultado["perfil"]["deseos"],
            distribucion_objetivo=resultado["perfil"]["distribucion_objetivo"],
            portafolio_optimo=resultado["portafolio"],
            valor_proyectado=resultado["valor_proyectado"],
            fondo_emergencia_valor=resultado["fondo_emergencia"],
            recomendacion=recomendacion,
            mensaje=generar_mensaje(resultado)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/catalogo")
def obtener_catalogo_inversiones():
    """Obtiene catálogo completo de inversiones"""
    try:
        catalogo = cargar_catalogo()
        if not catalogo:
            return {"mensaje": "Catálogo no disponible"}
        return {"inversiones": catalogo}
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health_check():
    """Verifica estado de conexión con Ollama"""
    try:
        response = chat(
            model=MODEL,
            messages=[{"role": "user", "content": "Hola"}],
            stream=False
        )
        return {"status": "OK", "modelo": MODEL}
    except Exception as e:
        return {"status": "ERROR", "detalle": str(e)}


@app.post("/analisis-inteligente")
def analisis_inteligente_route(payload: dict):
    """Ruta modular: análisis inteligente sin tocar /analizar existente."""
    try:
        resultado = generar_analisis_inteligente(payload)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============== EJECUTAR ===============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
