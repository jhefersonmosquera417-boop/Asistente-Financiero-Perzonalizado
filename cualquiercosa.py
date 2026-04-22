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