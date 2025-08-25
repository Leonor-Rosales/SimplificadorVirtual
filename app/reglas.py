import re

def contar_variables(expr):
    return len(set(re.findall(r"[A-Z]", expr)))


def simplificar_expresion(expr):
    pasos = []

    if contar_variables(expr) > 5:
        pasos.append({
            "ley": "Restricción del programa",
            "resultado": "⚠️ Solo puedes simplificar hasta 5 variables. Para más necesitas una suscripción."
        })
        return pasos

    pasos.append({"ley": "Función ingresada", "resultado": expr})

    reglas = [
        (r"\+0", "", "Ley de Identidad (A + 0 = A)"),
        (r"0\+", "", "Ley de Identidad (0 + A = A)"),
        (r"⋅1", "", "Ley de Identidad (A⋅1 = A)"),
        (r"1⋅", "", "Ley de Identidad (1⋅A = A)"),


        (r"[A-Z]⋅0", "0", "Ley de Anulación (A⋅0 = 0)"),
        (r"0⋅[A-Z]", "0", "Ley de Anulación (0⋅A = 0)"),
        (r"[A-Z]\+1", "1", "Ley de Anulación (A + 1 = 1)"),
        (r"1\+[A-Z]", "1", "Ley de Anulación (1 + A = 1)"),

        (r"([A-Z])\+\1", r"\1", "Ley de Idempotencia (A + A = A)"),
        (r"([A-Z])⋅\1", r"\1", "Ley de Idempotencia (A⋅A = A)"),

        (r"([A-Z])\+(\1′)", "1", "Ley del Complemento (A + A′ = 1)"),
        (r"([A-Z])⋅(\1′)", "0", "Ley del Complemento (A⋅A′ = 0)"),

        (r"([A-Z])′′", r"\1", "Ley de la Involución ((A′)′ = A)"),


        (r"([A-Z])\+\1⋅([A-Z])", r"\1", "Ley de Absorción (A + A⋅B = A)"),
        (r"([A-Z])\+([A-Z])⋅\1", r"\1", "Ley de Absorción (A + B⋅A = A)"),
        (r"([A-Z])⋅(\1\+[A-Z])", r"\1", "Ley de Absorción (A⋅(A + B) = A)"),


        (r"\(([^()]*)\+([^()]*)\)′", r"\1′⋅\2′", "Ley de De Morgan ((A+B)′ = A′⋅B′)"),
        (r"\(([^()]*)⋅([^()]*)\)′", r"\1′+\2′", "Ley de De Morgan ((A⋅B)′ = A′+B′)"),
    ]

    cambiado = True
    while cambiado:
        cambiado = False
        for patron, reemplazo, nombre in reglas:
            nueva = re.sub(patron, reemplazo, expr)
            if nueva != expr:
                pasos.append({"ley": nombre, "resultado": nueva})
                expr = nueva
                cambiado = True
                break


    pasos.append({"ley": "Resultado final", "resultado": expr})

    return pasos
