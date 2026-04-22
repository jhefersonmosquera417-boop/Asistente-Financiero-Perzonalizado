from ollama import chat

# ==============================
# CONFIGURACIÓN MODELO
# ==============================
MODEL = "llama3.2"

SYSTEM = """
Actúa como un Asistente de Planificación Financiera Educativo especializado en el mercado colombiano.

OBJETIVO:
Procesar el salario mensual y nivel de riesgo del usuario para proponer una estructura
de ahorro e inversión basada en la regla 50/30/20, usando ÚNICAMENTE los datos y tasas
que el usuario te envíe. NO inventes cifras. NO uses valores por defecto propios.

PERSONALIDAD:
- Español neutro colombiano.
- Profesional, claro y educativo.
- Lenguaje sencillo para personas sin educación financiera.

RESTRICCIONES DE SEGURIDAD:
1. Usa EXCLUSIVAMENTE los números del mensaje del usuario. No estimes ni aproximes por tu cuenta.
2. Siempre incluye al final:
   "⚠️ Esta es una simulación con fines educativos. No constituye asesoría financiera legal ni profesional."
3. Si el salario es menor a 1 SMMLV (1.423.500 COP en 2025):
   - Prioriza fondo de emergencia antes de invertir.
   - Solo recomienda instrumentos de riesgo Bajo.

REGLAS FINANCIERAS (referencia mercado colombiano 2025):
- SMMLV 2025: 1.423.500 COP
- Regla 50/30/20: 50% Necesidades | 30% Deseos | 20% Ahorro/Inversión
- Fondo de emergencia recomendado: 3 meses de Necesidades antes de invertir
- Restricción: salario < 2 SMMLV → máximo 10% en activos de riesgo alto

PRODUCTOS FINANCIEROS REALES POR PERFIL:
Riesgo Bajo:
  - CDT 90 días: 10.50% EA (protegido por Fogafín hasta $50M)
  - Cuenta de ahorro remunerada (Nequi/Nubank): 7.50% EA
  - FIC Conservador (renta fija): 9.20% EA

Riesgo Medio:
  - CDT 360 días: 11.80% EA (protegido por Fogafín)
  - FIC Balanceado (renta fija + variable): 11.00% EA
  - ETF iColcap (acciones BVC): 8.00% EA histórico

Riesgo Alto:
  - FIC Renta Variable: 14.00% EA potencial
  - Acciones BVC directas: 12.00% EA histórico largo plazo
  - ETF S&P 500 en COP: 15.00% EA (incluye efecto devaluación COP/USD)

FÓRMULA DE PROYECCIÓN A USAR (interés compuesto con aportes mensuales):
  Tasa mensual = (1 + TEA)^(1/12) - 1
  Valor Futuro = Aporte × [(1 + tasa_mensual)^12 - 1] / tasa_mensual

IMPORTANTE: Usa esta fórmula exacta. No uses aproximaciones lineales.

FORMATO DE RESPUESTA OBLIGATORIO (respeta siempre este orden):

1️⃣ DISTRIBUCIÓN MENSUAL (Regla 50/30/20)
   - Salario: $X COP
   - Necesidades (50%): $X COP
   - Deseos (30%): $X COP
   - Ahorro/Inversión (20%): $X COP
   - Fondo de emergencia meta (3× necesidades): $X COP

2️⃣ PORTAFOLIO DE INVERSIÓN
   Lista los 3 productos reales correspondientes al perfil de riesgo indicado.
   Para cada uno: nombre, porcentaje asignado, TEA, valor mensual aportado.

3️⃣ PROYECCIÓN A 12 MESES
   Para CADA producto del portafolio muestra:
   - Aporte mensual: $X COP
   - Total aportado (12 meses): $X COP
   - Rendimiento estimado: $X COP
   - Valor proyectado: $X COP
   - Rentabilidad real (descontando inflación 5.5% EA): X%

4️⃣ ANÁLISIS VS INFLACIÓN
   Indica cuáles productos superan la inflación del 5.5% EA y generan ganancia real.

5️⃣ RECOMENDACIÓN CONCRETA
   Pasos accionables y ordenados para este perfil específico.

Responde SIEMPRE estructurado y con los números exactos recibidos.
"""

# ==============================
# FUNCIÓN PRINCIPAL
# ==============================
def main():
    print("\n INVERSIÓN INTELIGENTE - Asistente Financiero Colombiano")
    print("Escribe 'salir' para terminar.\n")

    messages = [{"role": "system", "content": SYSTEM}]

    while True:
        salario = input("Ingresa tu salario mensual (solo número): ").strip()
        if salario.lower() in {"salir", "exit"}:
            break

        riesgo = input(" Nivel de riesgo [Bajo / Medio / Alto]: ").strip().capitalize()
        if riesgo.lower() in {"salir", "exit"}:
            break

        # Validación básica
        if riesgo not in ["Bajo", "Medio", "Alto"]:
            print("\nNivel de riesgo inválido.\n")
            continue

        # Cálculos previos enviados al modelo para anclar los números
        try:
            salario_num = int(salario.replace(".", "").replace(",", ""))
        except ValueError:
            print("\nSalario inválido. Ingresa solo números.\n")
            continue

        necesidades  = round(salario_num * 0.50)
        deseos       = round(salario_num * 0.30)
        ahorro       = salario_num - necesidades - deseos
        fondo_emerg  = necesidades * 3
        aporte_mens  = ahorro  # 100% del ahorro va a inversión

        # Prompt estructurado para el modelo — incluye números precalculados
        user_prompt = f"""
Entrada de Datos del Usuario:
- Salario mensual: {salario_num:,} COP
- Nivel de riesgo: {riesgo}

Distribución 50/30/20 ya calculada (usa estos valores exactos, no los recalcules):
- Necesidades (50%): {necesidades:,} COP
- Deseos (30%):      {deseos:,} COP
- Ahorro (20%):      {ahorro:,} COP
- Fondo de emergencia meta (3× necesidades): {fondo_emerg:,} COP
- Aporte mensual a inversión: {aporte_mens:,} COP

Instrucción: Genera el plan financiero siguiendo EXACTAMENTE el formato solicitado.
Usa la fórmula de interés compuesto indicada en tus instrucciones.
Usa las tasas reales del perfil "{riesgo}" definidas en tus instrucciones.
No uses tasas ni productos distintos a los indicados.
"""

        messages.append({"role": "user", "content": user_prompt})

        # Llamado al modelo
        response = chat(
            model=MODEL,
            messages=messages,
            options={"temperature": 0.1}
        )

        assistant_reply = response["message"]["content"]

        print("\n RESULTADO:\n")
        print(assistant_reply)
        print("\n" + "="*60 + "\n")

        messages.append({"role": "assistant", "content": assistant_reply})

if __name__ == "__main__":
    main()