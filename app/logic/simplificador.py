from .nodo import Nodo


def simplificar_arbol(arbol):
    pasos_globales = []

    def recorrer(nodo, pasos_de_esta_pasada):
        if nodo is None:
            return None

        # 1. Simplificar hijos primero (recursión)
        if nodo.izquierda:
            nodo.izquierda = recorrer(nodo.izquierda, pasos_de_esta_pasada)
        if nodo.derecha:
            nodo.derecha = recorrer(nodo.derecha, pasos_de_esta_pasada)

        # 2. Normalización Conmutativa
        if nodo.valor in ["+", "*"] and nodo.izquierda and nodo.derecha:
            if str(nodo.izquierda) > str(nodo.derecha):
                nodo.izquierda, nodo.derecha = nodo.derecha, nodo.izquierda

        antes = str(nodo)

        # 3. Aplicar Leyes de Simplificación

        # ... (Idempotencia, Identidad, Anulación, Complemento, Doble Negación - sin cambios) ...

        # Ley Idempotencia (A+A = A) (A*A = A)
        if nodo.valor in ["+", "*"] and nodo.izquierda and nodo.derecha:
            if str(nodo.izquierda) == str(nodo.derecha):
                nuevo_nodo = nodo.izquierda
                pasos_de_esta_pasada.append({"ley": "Idempotencia", "antes": antes, "despues": str(nuevo_nodo)})
                return nuevo_nodo

        # Ley Identidad y Anulación
        if nodo.valor == "+":  # OR
            if str(nodo.izquierda) == "0":
                nuevo_nodo = nodo.derecha
                pasos_de_esta_pasada.append({"ley": "Identidad (0+A=A)", "antes": antes, "despues": str(nuevo_nodo)})
                return nuevo_nodo
            if str(nodo.derecha) == "0":
                nuevo_nodo = nodo.izquierda
                pasos_de_esta_pasada.append({"ley": "Identidad (A+0=A)", "antes": antes, "despues": str(nuevo_nodo)})
                return nuevo_nodo
            if str(nodo.izquierda) == "1" or str(nodo.derecha) == "1":
                nuevo_nodo = Nodo("1")
                pasos_de_esta_pasada.append({"ley": "Anulación (A+1=1)", "antes": antes, "despues": "1"})
                return nuevo_nodo

        if nodo.valor == "*":  # AND
            if str(nodo.izquierda) == "0" or str(nodo.derecha) == "0":
                nuevo_nodo = Nodo("0")
                pasos_de_esta_pasada.append({"ley": "Anulación (A*0=0)", "antes": antes, "despues": "0"})
                return nuevo_nodo
            if str(nodo.izquierda) == "1":
                nuevo_nodo = nodo.derecha
                pasos_de_esta_pasada.append({"ley": "Identidad (1*A=A)", "antes": antes, "despues": str(nuevo_nodo)})
                return nuevo_nodo
            if str(nodo.derecha) == "1":
                nuevo_nodo = nodo.izquierda
                pasos_de_esta_pasada.append({"ley": "Identidad (A*1=A)", "antes": antes, "despues": str(nuevo_nodo)})
                return nuevo_nodo

        # Ley Complemento (A+A' = 1) (A*A' = 0)
        if nodo.valor == "+" and nodo.izquierda and nodo.derecha:
            if str(nodo.izquierda) == f"~({str(nodo.derecha)})" or str(nodo.derecha) == f"~({str(nodo.izquierda)})":
                nuevo_nodo = Nodo("1")
                pasos_de_esta_pasada.append({"ley": "Complemento (A+~A=1)", "antes": antes, "despues": "1"})
                return nuevo_nodo
        if nodo.valor == "*" and nodo.izquierda and nodo.derecha:
            if str(nodo.izquierda) == f"~({str(nodo.derecha)})" or str(nodo.derecha) == f"~({str(nodo.izquierda)})":
                nuevo_nodo = Nodo("0")
                pasos_de_esta_pasada.append({"ley": "Complemento (A*~A=0)", "antes": antes, "despues": "0"})
                return nuevo_nodo

        # Ley Doble negación (A'' = A)
        if nodo.valor == "~" and nodo.izquierda.valor == "~":
            nuevo_nodo = nodo.izquierda.izquierda
            pasos_de_esta_pasada.append({"ley": "Doble negación", "antes": antes, "despues": str(nuevo_nodo)})
            return nuevo_nodo

        # --- LEY DE ABSORCIÓN (Actualizada) ---
        if nodo.valor == "+":
            # (A*B) + A
            if nodo.izquierda and nodo.izquierda.valor == "*":
                if str(nodo.derecha) == str(nodo.izquierda.izquierda) or str(nodo.derecha) == str(
                        nodo.izquierda.derecha):
                    nuevo_nodo = nodo.derecha
                    pasos_de_esta_pasada.append(
                        {"ley": "Absorción (AB+A=A)", "antes": antes, "despues": str(nuevo_nodo)})
                    return nuevo_nodo

            # (NUEVO) Absorción Asociativa: ((A*B) + Y) + A
            if nodo.izquierda.valor == "+":
                X = nodo.izquierda.izquierda
                Y = nodo.izquierda.derecha
                Z = nodo.derecha

                # Caso 1: ( (A*B) + Y ) + A  -> A + Y
                if X.valor == "*" and (str(X.izquierda) == str(Z) or str(X.derecha) == str(Z)):
                    nuevo_nodo = Nodo("+", Z, Y)
                    pasos_de_esta_pasada.append(
                        {"ley": "Absorción (Asociativa)", "antes": antes, "despues": str(nuevo_nodo)})
                    # (CORREGIDO) Pasar el argumento
                    return recorrer(nuevo_nodo, pasos_de_esta_pasada)

                # Caso 2: ( X + (A*B) ) + A -> A + X
                if Y.valor == "*" and (str(Y.izquierda) == str(Z) or str(Y.derecha) == str(Z)):
                    nuevo_nodo = Nodo("+", Z, X)
                    pasos_de_esta_pasada.append(
                        {"ley": "Absorción (Asociativa)", "antes": antes, "despues": str(nuevo_nodo)})
                    # (CORREGIDO) Pasar el argumento
                    return recorrer(nuevo_nodo, pasos_de_esta_pasada)

        if nodo.valor == "*":
            # (A+B) * A
            if nodo.izquierda and nodo.izquierda.valor == "+":
                if str(nodo.derecha) == str(nodo.izquierda.izquierda) or str(nodo.derecha) == str(
                        nodo.izquierda.derecha):
                    nuevo_nodo = nodo.derecha
                    pasos_de_esta_pasada.append(
                        {"ley": "Absorción ((A+B)A=A)", "antes": antes, "despues": str(nuevo_nodo)})
                    return nuevo_nodo

        # Absorción (A + ~A*B = A+B)
        if nodo.valor == "+":
            if nodo.izquierda.valor == "*" and nodo.izquierda.izquierda.valor == "~":
                if str(nodo.derecha) == str(nodo.izquierda.izquierda.izquierda):
                    nuevo_nodo = Nodo("+", nodo.derecha, nodo.izquierda.derecha)
                    pasos_de_esta_pasada.append(
                        {"ley": "Absorción (~AB+A=A+B)", "antes": antes, "despues": str(nuevo_nodo)})
                    return nuevo_nodo

        # --- LEY DE MORGAN ---
        if nodo.valor == "~" and nodo.izquierda:
            if nodo.izquierda.valor == "+":
                nuevo = Nodo("*", Nodo("~", nodo.izquierda.izquierda), Nodo("~", nodo.izquierda.derecha))
                pasos_de_esta_pasada.append({"ley": "De Morgan", "antes": antes, "despues": str(nuevo)})
                return nuevo
            if nodo.izquierda.valor == "*":
                nuevo = Nodo("+", Nodo("~", nodo.izquierda.izquierda), Nodo("~", nodo.izquierda.derecha))
                pasos_de_esta_pasada.append({"ley": "De Morgan", "antes": antes, "despues": str(nuevo)})
                return nuevo

        # --- LEY DISTRIBUTIVA ---
        if nodo.valor == "*":
            # (B+C) * A
            if nodo.izquierda and nodo.izquierda.valor == "+":
                der = nodo.derecha
                izq_izq = nodo.izquierda.izquierda
                izq_der = nodo.izquierda.derecha
                nuevo = Nodo("+", Nodo("*", izq_izq, der), Nodo("*", izq_der, der))
                pasos_de_esta_pasada.append({"ley": "Distributiva", "antes": antes, "despues": str(nuevo)})
                return nuevo

        if nodo.valor == "+":
            # (A*B) + (A*C)
            if nodo.izquierda.valor == "*" and nodo.derecha.valor == "*":
                if str(nodo.izquierda.izquierda) == str(nodo.derecha.izquierda):
                    A = nodo.izquierda.izquierda
                    B = nodo.izquierda.derecha
                    C = nodo.derecha.derecha
                    nuevo = Nodo("*", A, Nodo("+", B, C))
                    pasos_de_esta_pasada.append({"ley": "Distributiva (Factor)", "antes": antes, "despues": str(nuevo)})
                    return nuevo

        if nodo.valor == "*":
            # (A+B)*(A+C)
            if nodo.izquierda.valor == "+" and nodo.derecha.valor == "+":
                if str(nodo.izquierda.izquierda) == str(nodo.derecha.izquierda):
                    A = nodo.izquierda.izquierda
                    B = nodo.izquierda.derecha
                    C = nodo.derecha.derecha
                    nuevo = Nodo("+", A, Nodo("*", B, C))
                    pasos_de_esta_pasada.append({"ley": "Distributiva (A+BC)", "antes": antes, "despues": str(nuevo)})
                    return nuevo

        return nodo

    # --- Bucle principal de simplificación ---
    arbol_actual = arbol
    while True:
        pasos_de_ronda = []
        arbol_nuevo = recorrer(arbol_actual, pasos_de_ronda)

        if not pasos_de_ronda:
            break

        pasos_globales.extend(pasos_de_ronda)
        arbol_actual = arbol_nuevo

    return arbol_actual, pasos_globales