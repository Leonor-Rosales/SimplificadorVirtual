from .nodo import Nodo

def aplicar_reglas(nodo):
    if nodo is None:
        return None

    # Simplificar recursivamente
    nodo.izquierda = aplicar_reglas(nodo.izquierda)
    nodo.derecha = aplicar_reglas(nodo.derecha)

    # ---- LEYES ----

    # Idempotencia: A + A = A, A * A = A
    if nodo.valor == '+' and nodo.izquierda and nodo.derecha:
        if str(nodo.izquierda) == str(nodo.derecha):
            return nodo.izquierda
    if nodo.valor == '*' and nodo.izquierda and nodo.derecha:
        if str(nodo.izquierda) == str(nodo.derecha):
            return nodo.izquierda

    # Identidad y elemento nulo
    if nodo.valor == '+':
        if nodo.izquierda and nodo.izquierda.valor == '0':
            return nodo.derecha
        if nodo.derecha and nodo.derecha.valor == '0':
            return nodo.izquierda
        if nodo.izquierda and nodo.izquierda.valor == '1':
            return Nodo('1')
        if nodo.derecha and nodo.derecha.valor == '1':
            return Nodo('1')

    if nodo.valor == '*':
        if nodo.izquierda and nodo.izquierda.valor == '1':
            return nodo.derecha
        if nodo.derecha and nodo.derecha.valor == '1':
            return nodo.izquierda
        if nodo.izquierda and nodo.izquierda.valor == '0':
            return Nodo('0')
        if nodo.derecha and nodo.derecha.valor == '0':
            return Nodo('0')

    # Complemento
    if nodo.valor == '+':
        if (nodo.izquierda and nodo.derecha and
            nodo.izquierda.valor == '!' + str(nodo.derecha.valor)):
            return Nodo('1')
        if (nodo.izquierda and nodo.derecha and
            nodo.derecha.valor == '!' + str(nodo.izquierda.valor)):
            return Nodo('1')

    if nodo.valor == '*':
        if (nodo.izquierda and nodo.derecha and
            nodo.izquierda.valor == '!' + str(nodo.derecha.valor)):
            return Nodo('0')
        if (nodo.izquierda and nodo.derecha and
            nodo.derecha.valor == '!' + str(nodo.izquierda.valor)):
            return Nodo('0')

    # Doble negación
    if nodo.valor.startswith('!!'):
        return Nodo(nodo.valor[2:])

    # Absorción
    if nodo.valor == '+':
        if (nodo.izquierda and nodo.derecha and nodo.derecha.valor == '*'):
            if (str(nodo.izquierda) == str(nodo.derecha.izquierda) or
                str(nodo.izquierda) == str(nodo.derecha.derecha)):
                return nodo.izquierda
        if (nodo.derecha and nodo.izquierda and nodo.izquierda.valor == '*'):
            if (str(nodo.derecha) == str(nodo.izquierda.izquierda) or
                str(nodo.derecha) == str(nodo.izquierda.derecha)):
                return nodo.derecha

    if nodo.valor == '*':
        if (nodo.izquierda and nodo.derecha and nodo.derecha.valor == '+'):
            if (str(nodo.izquierda) == str(nodo.derecha.izquierda) or
                str(nodo.izquierda) == str(nodo.derecha.derecha)):
                return nodo.izquierda
        if (nodo.derecha and nodo.izquierda and nodo.izquierda.valor == '+'):
            if (str(nodo.derecha) == str(nodo.izquierda.izquierda) or
                str(nodo.derecha) == str(nodo.izquierda.derecha)):
                return nodo.derecha

    # Conmutativa (normalizar el orden alfabético para evitar duplicados)
    if nodo.valor in ['+', '*']:
        if nodo.izquierda and nodo.derecha:
            if str(nodo.izquierda) > str(nodo.derecha):
                nodo.izquierda, nodo.derecha = nodo.derecha, nodo.izquierda

    # 🔹 Quitamos la ley distributiva y no forzamos asociativa
    # (ya la maneja naturalmente el árbol al construirse)

    return nodo


def simplificar_arbol(nodo):
    if nodo is None:
        return None
    anterior = None
    while str(anterior) != str(nodo):
        anterior = nodo
        nodo = aplicar_reglas(nodo)
    return nodo
