import re

def contar_variables(expr):
    # Solo letras mayúsculas como variables
    return len(set(re.findall(r"[A-Z]", expr)))


def simplificar_expresion(expr):
    pasos = []

    # 🔹 Paso 0: validar número de variables
    if contar_variables(expr) > 5:
        pasos.append({
            "ley": "Restricción del programa",
            "resultado": "⚠️ Solo puedes simplificar hasta 5 variables. Para más necesitas una suscripción."
        })
        return pasos

    # 🔹 Mostrar la función inicial
    pasos.append({"ley": "Función ingresada", "resultado": expr})

    # --- LEYES BÁSICAS DEL ÁLGEBRA BOOLEANA ---
    reglas = [
        # Identidad
        (r"\+0", "", "Ley de Identidad (A + 0 = A)"),
        (r"0\+", "", "Ley de Identidad (0 + A = A)"),
        (r"⋅1", "", "Ley de Identidad (A⋅1 = A)"),
        (r"1⋅", "", "Ley de Identidad (1⋅A = A)"),

        # Anulación
        (r"[A-Z]⋅0", "0", "Ley de Anulación (A⋅0 = 0)"),
        (r"0⋅[A-Z]", "0", "Ley de Anulación (0⋅A = 0)"),
        (r"[A-Z]\+1", "1", "Ley de Anulación (A + 1 = 1)"),
        (r"1\+[A-Z]", "1", "Ley de Anulación (1 + A = 1)"),

        # Idempotencia
        (r"([A-Z])\+\1", r"\1", "Ley de Idempotencia (A + A = A)"),
        (r"([A-Z])⋅\1", r"\1", "Ley de Idempotencia (A⋅A = A)"),

        # Complemento
        (r"([A-Z])\+(\1′)", "1", "Ley del Complemento (A + A′ = 1)"),
        (r"([A-Z])⋅(\1′)", "0", "Ley del Complemento (A⋅A′ = 0)"),

        # Involución
        (r"([A-Z])′′", r"\1", "Ley de la Involución ((A′)′ = A)"),

        # Absorción
        (r"([A-Z])\+\1⋅([A-Z])", r"\1", "Ley de Absorción (A + A⋅B = A)"),
        (r"([A-Z])\+([A-Z])⋅\1", r"\1", "Ley de Absorción (A + B⋅A = A)"),
        (r"([A-Z])⋅(\1\+[A-Z])", r"\1", "Ley de Absorción (A⋅(A + B) = A)"),

        # De Morgan
        (r"\(([^()]*)\+([^()]*)\)′", r"\1′⋅\2′", "Ley de De Morgan ((A+B)′ = A′⋅B′)"),
        (r"\(([^()]*)⋅([^()]*)\)′", r"\1′+\2′", "Ley de De Morgan ((A⋅B)′ = A′+B′)"),
    ]

    # 🔹 Aplicar reglas iterativamente
    cambiado = True
    while cambiado:
        cambiado = False
        for patron, reemplazo, nombre in reglas:
            nueva = re.sub(patron, reemplazo, expr)
            if nueva != expr:
                pasos.append({"ley": nombre, "resultado": nueva})
                expr = nueva
                cambiado = True
                break  # volvemos a empezar desde arriba

    # 🔹 Resultado final
    pasos.append({"ley": "Resultado final", "resultado": expr})

    return pasos
