import ollama
import json
import os

MODELO = "llama3.2"
ARCHIVO_DATOS = "dataset_finanzas_colombia.jsonl"

def cargar_contexto_desde_archivo():
    mensajes = []

    prompt = """
    Eres un planificador financiero automatizado para Colombia.

    Debes analizar: salario, riesgo, deudas y objetivos.

    REGLAS ESTRICTAS:

    1. Si hay deudas > 0:
       - Prioriza pagar deudas antes de invertir.
       - Asigna mínimo 20% del ahorro a deudas.

    2. Si el objetivo incluye "casa", "vivienda" o "hogar":
       - Crea categoría "ahorro_vivienda".
       - Asigna entre 30% y 50% del ahorro a vivienda.

    3. Siempre separar ahorro en:
       - fondo_emergencia
       - ahorro_vivienda (si aplica)
       - inversion

    4. Fondo de emergencia obligatorio hasta completar 3 meses de salario.

    5. REGLA 50/30/20 base:
       - necesidades 50%
       - deseos 30%
       - ahorro 20% mínimo

    6. Riesgo:
       - bajo: cdt, bonos, oro
       - medio: fondos, acciones
       - alto: cripto, emprendimiento

    7. Nunca exceder el dinero disponible.

    FORMATO JSON:
    {
      "distribucion_mensual": {
        "necesidades": 0,
        "deseos": 0,
        "ahorro_inversion": 0
      },
      "ahorro_detallado": {
        "deuda": 0,
        "fondo_emergencia": 0,
        "ahorro_vivienda": 0,
        "inversion": 0
      },
      "portafolio_inversion": {
        "cdt": 0,
        "fondos_inversion": 0,
        "acciones": 0,
        "bonos": 0,
        "criptomonedas": 0,
        "oro": 0
      },
      "proyeccion_12_meses": {
        "ahorro_total": 0
      },
      "advertencia": ""
    }

    Responde SOLO JSON válido.
    """

    mensajes.append({"role": "system", "content": prompt})

    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            for linea in f:
                d = json.loads(linea)
                mensajes.append({"role": "user", "content": d["input"]})
                mensajes.append({"role": "assistant", "content": d["output"]})

    return mensajes

def ajustar(plan, salario, deudas, objetivo):
    necesidades = int(salario * 0.5)
    deseos = int(salario * 0.3)
    ahorro = salario - necesidades - deseos

    plan["distribucion_mensual"] = {
        "necesidades": necesidades,
        "deseos": deseos,
        "ahorro_inversion": ahorro
    }

    det = {
        "deuda": 0,
        "fondo_emergencia": 0,
        "ahorro_vivienda": 0,
        "inversion": 0
    }

    if deudas > 0:
        det["deuda"] = int(ahorro * 0.3)

    if "casa" in objetivo or "vivienda" in objetivo:
        det["ahorro_vivienda"] = int(ahorro * 0.4)

    restante = ahorro - det["deuda"] - det["ahorro_vivienda"]

    det["fondo_emergencia"] = int(restante * 0.5)
    det["inversion"] = restante - det["fondo_emergencia"]

    plan["ahorro_detallado"] = det

    inv = det["inversion"]

    plan["portafolio_inversion"] = {
        "cdt": int(inv * 0.4),
        "fondos_inversion": int(inv * 0.3),
        "acciones": int(inv * 0.2),
        "bonos": 0,
        "criptomonedas": 0,
        "oro": int(inv * 0.1)
    }

    plan["proyeccion_12_meses"] = {
        "ahorro_total": ahorro * 12
    }

    plan["advertencia"] = "Simulación educativa. No es asesoría financiera profesional."

    return plan

def main():
    historial = cargar_contexto_desde_archivo()

    print("\n=== MOTOR FINANCIERO INTELIGENTE ===\n")

    while True:
        entrada = input("salario,riesgo,deudas,objetivo:\n> ")

        if entrada.lower() == "salir":
            break

        try:
            partes = entrada.split(",")
            salario = int(partes[0])
            riesgo = partes[1].strip()
            deudas = int(partes[2])
            objetivo = partes[3].lower()
        except:
            print("Entrada inválida")
            continue

        msgs = historial.copy()
        msgs.append({"role": "user", "content": entrada})

        try:
            r = ollama.chat(
                model=MODELO,
                messages=msgs,
                format="json",
                options={"temperature": 0.1}
            )

            plan = json.loads(r["message"]["content"])
            plan = ajustar(plan, salario, deudas, objetivo)

            print(json.dumps(plan, indent=2, ensure_ascii=False))

        except:
            print("Error en generación")

if __name__ == "__main__":
    main()