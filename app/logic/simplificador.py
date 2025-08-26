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

        # 🔹 Idempotencia
        if nodo.valor in ["+", "*"] and nodo.izquierda and nodo.derecha:
            if str(nodo.izquierda) == str(nodo.derecha):
                pasos.append({"ley": "Idempotencia", "antes": antes, "despues": str(nodo.izquierda)})
                return recorrer(nodo.izquierda)

        # 🔹 Elemento nulo e identidad
        if nodo.valor == "+":
            if str(nodo.izquierda) == "0":
                pasos.append({"ley": "Elemento nulo", "antes": antes, "despues": str(nodo.derecha)})
                return recorrer(nodo.derecha)
            if str(nodo.derecha) == "0":
                pasos.append({"ley": "Elemento nulo", "antes": antes, "despues": str(nodo.izquierda)})
                return recorrer(nodo.izquierda)
            if str(nodo.izquierda) == "1" or str(nodo.derecha) == "1":
                pasos.append({"ley": "Elemento identidad", "antes": antes, "despues": "1"})
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

        # 🔹 Complemento
        if nodo.valor == "+" and (str(nodo.izquierda) == f"~({nodo.derecha})" or str(nodo.derecha) == f"~({nodo.izquierda})"):
            pasos.append({"ley": "Complemento", "antes": antes, "despues": "1"})
            return Nodo("1")
        if nodo.valor == "*" and (str(nodo.izquierda) == f"~({nodo.derecha})" or str(nodo.derecha) == f"~({nodo.izquierda})"):
            pasos.append({"ley": "Complemento", "antes": antes, "despues": "0"})
            return Nodo("0")

        # 🔹 Doble negación (Involución)
        if nodo.valor == "~" and nodo.izquierda.valor == "~":
            pasos.append({"ley": "Doble negación", "antes": antes, "despues": str(nodo.izquierda.izquierda)})
            return recorrer(nodo.izquierda.izquierda)

        # 🔹 Absorción
        if nodo.valor == "+":
            if nodo.derecha and nodo.derecha.valor == "*":
                if str(nodo.izquierda) == str(nodo.derecha.izquierda) or str(nodo.izquierda) == str(nodo.derecha.derecha):
                    pasos.append({"ley": "Absorción", "antes": antes, "despues": str(nodo.izquierda)})
                    return recorrer(nodo.izquierda)
            if nodo.izquierda and nodo.izquierda.valor == "*":
                if str(nodo.derecha) == str(nodo.izquierda.izquierda) or str(nodo.derecha) == str(nodo.izquierda.derecha):
                    pasos.append({"ley": "Absorción", "antes": antes, "despues": str(nodo.derecha)})
                    return recorrer(nodo.derecha)
        if nodo.valor == "*":
            if nodo.derecha and nodo.derecha.valor == "+":
                if str(nodo.izquierda) == str(nodo.derecha.izquierda) or str(nodo.izquierda) == str(nodo.derecha.derecha):
                    pasos.append({"ley": "Absorción", "antes": antes, "despues": str(nodo.izquierda)})
                    return recorrer(nodo.izquierda)
            if nodo.izquierda and nodo.izquierda.valor == "+":
                if str(nodo.derecha) == str(nodo.izquierda.izquierda) or str(nodo.derecha) == str(nodo.izquierda.derecha):
                    pasos.append({"ley": "Absorción", "antes": antes, "despues": str(nodo.derecha)})
                    return recorrer(nodo.derecha)

        # 🔹 De Morgan
        if nodo.valor == "~" and nodo.izquierda:
            if nodo.izquierda.valor == "+":
                nuevo = Nodo("*", Nodo("~", nodo.izquierda.izquierda), Nodo("~", nodo.izquierda.derecha))
                pasos.append({"ley": "De Morgan", "antes": antes, "despues": str(nuevo)})
                return recorrer(nuevo)
            if nodo.izquierda.valor == "*":
                nuevo = Nodo("+", Nodo("~", nodo.izquierda.izquierda), Nodo("~", nodo.izquierda.derecha))
                pasos.append({"ley": "De Morgan", "antes": antes, "despues": str(nuevo)})
                return recorrer(nuevo)

        return nodo

    cambio = True
    arbol_final = arbol
    while cambio:
        arbol_nuevo = recorrer(arbol_final)
        if str(arbol_nuevo) == str(arbol_final):
            cambio = False
        arbol_final = arbol_nuevo

    return arbol_final, pasos
