from .nodo import Nodo

def simplificar_arbol(arbol):
    pasos = []

    def recorrer(nodo):
        if nodo is None:
            return None

        if nodo.izquierda:
            nodo.izquierda = recorrer(nodo.izquierda)
        if nodo.derecha:
            nodo.derecha = recorrer(nodo.derecha)

        antes = str(nodo)

        # Idempotencia: A + A = A, A * A = A
        if nodo.valor in ["+", "*"] and nodo.izquierda and nodo.derecha:
            if str(nodo.izquierda) == str(nodo.derecha):
                pasos.append({"ley": "Idempotencia", "antes": antes, "despues": str(nodo.izquierda)})
                return recorrer(nodo.izquierda)

        #  Identidad y elemento nulo
        if nodo.valor == "+":
            if str(nodo.izquierda) == "0":
                pasos.append({"ley": "Elemento nulo", "antes": antes, "despues": str(nodo.derecha)})
                return recorrer(nodo.derecha)
            if str(nodo.derecha) == "0":
                pasos.append({"ley": "Elemento nulo", "antes": antes, "despues": str(nodo.izquierda)})
                return recorrer(nodo.izquierda)
            if str(nodo.izquierda) == "1" or str(nodo.derecha) == "1":
                pasos.append({"ley": "Identidad", "antes": antes, "despues": "1"})
                return Nodo("1")

        if nodo.valor == "*":
            if str(nodo.izquierda) == "0" or str(nodo.derecha) == "0":
                pasos.append({"ley": "Elemento nulo", "antes": antes, "despues": "0"})
                return Nodo("0")
            if str(nodo.izquierda) == "1":
                pasos.append({"ley": "Elemento identidad", "antes": antes, "despues": str(nodo.derecha)})
                return recorrer(nodo.derecha)
            if str(nodo.derecha) == "1":
                pasos.append({"ley": "Elemento identidad", "antes": antes, "despues": str(nodo.izquierda)})
                return recorrer(nodo.izquierda)

        # Complemento
        if nodo.valor == "+" and (
            str(nodo.izquierda) == f"~({nodo.derecha})" or str(nodo.derecha) == f"~({nodo.izquierda})"
        ):
            pasos.append({"ley": "Complemento", "antes": antes, "despues": "1"})
            return Nodo("1")
        if nodo.valor == "*" and (
            str(nodo.izquierda) == f"~({nodo.derecha})" or str(nodo.derecha) == f"~({nodo.izquierda})"
        ):
            pasos.append({"ley": "Complemento", "antes": antes, "despues": "0"})
            return Nodo("0")

        # Doble negación
        if nodo.valor == "~" and nodo.izquierda and nodo.izquierda.valor == "~":
            pasos.append({"ley": "Doble negación", "antes": antes, "despues": str(nodo.izquierda.izquierda)})
            return recorrer(nodo.izquierda.izquierda)

        # Ley de absorción
        if nodo.valor == "+" and nodo.izquierda and nodo.derecha:
            izq, der = str(nodo.izquierda), str(nodo.derecha)
            if "*" in der and izq in der:  # A + A*B = A
                pasos.append({"ley": "Absorción", "antes": antes, "despues": izq})
                return recorrer(nodo.izquierda)
            if "*" in izq and der in izq:  # A*B + A = A
                pasos.append({"ley": "Absorción", "antes": antes, "despues": der})
                return recorrer(nodo.derecha)

        if nodo.valor == "*" and nodo.izquierda and nodo.derecha:
            izq, der = str(nodo.izquierda), str(nodo.derecha)
            if "+" in der and izq in der:  # A * (A+B) = A
                pasos.append({"ley": "Absorción", "antes": antes, "despues": izq})
                return recorrer(nodo.izquierda)
            if "+" in izq and der in izq:  # (A+B) * A = A
                pasos.append({"ley": "Absorción", "antes": antes, "despues": der})
                return recorrer(nodo.derecha)

        # Conmutativa: A + B = B + A, A * B = B * A
        if nodo.valor in ["+", "*"] and str(nodo.izquierda) > str(nodo.derecha):
            pasos.append({"ley": "Conmutativa", "antes": antes, "despues": f"({nodo.derecha}{nodo.valor}{nodo.izquierda})"})
            return Nodo(nodo.valor, nodo.derecha, nodo.izquierda)

        # Asociativa (ejemplo para +)
        if nodo.valor == "+" and nodo.derecha and nodo.derecha.valor == "+":
            pasos.append({"ley": "Asociativa", "antes": antes, "despues": f"(({nodo.izquierda}+{nodo.derecha.izquierda})+{nodo.derecha.derecha})"})
            return Nodo("+", Nodo("+", nodo.izquierda, nodo.derecha.izquierda), nodo.derecha.derecha)

        # Distributiva: A*(B+C) = A*B + A*C
        if nodo.valor == "*" and nodo.derecha and nodo.derecha.valor == "+":
            pasos.append({"ley": "Distributiva", "antes": antes, "despues": f"({nodo.izquierda}*{nodo.derecha.izquierda}+{nodo.izquierda}*{nodo.derecha.derecha})"})
            return Nodo("+", Nodo("*", nodo.izquierda, nodo.derecha.izquierda), Nodo("*", nodo.izquierda, nodo.derecha.derecha))
        if nodo.valor == "*" and nodo.izquierda and nodo.izquierda.valor == "+":
            pasos.append({"ley": "Distributiva", "antes": antes, "despues": f"({nodo.izquierda.izquierda}*{nodo.derecha}+{nodo.izquierda.derecha}*{nodo.derecha})"})
            return Nodo("+", Nodo("*", nodo.izquierda.izquierda, nodo.derecha), Nodo("*", nodo.izquierda.derecha, nodo.derecha))

        # De Morgan
        if nodo.valor == "~" and nodo.izquierda and nodo.izquierda.valor in ["+", "*"]:
            if nodo.izquierda.valor == "+":
                pasos.append({"ley": "De Morgan", "antes": antes, "despues": f"(~{nodo.izquierda.izquierda} * ~{nodo.izquierda.derecha})"})
                return Nodo("*", Nodo("~", nodo.izquierda.izquierda), Nodo("~", nodo.izquierda.derecha))
            if nodo.izquierda.valor == "*":
                pasos.append({"ley": "De Morgan", "antes": antes, "despues": f"(~{nodo.izquierda.izquierda} + ~{nodo.izquierda.derecha})"})
                return Nodo("+", Nodo("~", nodo.izquierda.izquierda), Nodo("~", nodo.izquierda.derecha))

        return nodo

    cambio = True
    arbol_final = arbol
    while cambio:
        arbol_nuevo = recorrer(arbol_final)
        if str(arbol_nuevo) == str(arbol_final):
            cambio = False
        arbol_final = arbol_nuevo

    return arbol_final, pasos
