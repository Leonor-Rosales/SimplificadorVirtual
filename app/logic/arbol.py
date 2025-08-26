import re
from .nodo import Nodo

def validar_expresion(expresion):
    if not expresion.strip():
        return "La expresión no puede estar vacía."

    expr = expresion.replace(" ", "")

    if not re.fullmatch(r"[A-Z01~+*()]*", expr):
        return "La expresión contiene caracteres inválidos."

    #se comprea el balanceo
    paren = 0
    for c in expr:
        if c == "(":
            paren += 1
        elif c == ")":
            paren -= 1
        if paren < 0:
            return "Paréntesis desbalanceados: se cerró uno que no estaba abierto."
    if paren != 0:
        return "Paréntesis desbalanceados: falta cerrar algún paréntesis."

    #Se verifican los operadores
    operadores = "+*"
    prev = ""
    for c in expr:
        if c in operadores and prev in operadores:
            return f"Operadores consecutivos no permitidos: '{prev}{c}'"
        prev = c

    # verificar si la funcion empieza con *
    if expr[0] in "+*" or expr[-1] in "+*":
        return "La expresión no puede comenzar ni terminar con '+' o '*'"

    return None  


def construir_arbol(expresion):
    tokens = list(expresion.replace(" ", ""))
    pos = [0]

    def siguiente_token():
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def consumir(token_esperado=None):
        t = siguiente_token()
        if t is None:
            return None
        if token_esperado and t != token_esperado:
            raise ValueError(f"Se esperaba '{token_esperado}' pero se encontró '{t}'")
        pos[0] += 1
        return t

    def parse_factor():
        t = siguiente_token()
        if t == "~":
            consumir("~")
            return Nodo("~", parse_factor())
        elif t == "(":
            consumir("(")
            nodo = parse_expresion()
            consumir(")")
            return nodo
        else:
            return Nodo(consumir())

    def parse_producto():
        nodo = parse_factor()
        while siguiente_token() == "*":
            consumir("*")
            nodo = Nodo("*", nodo, parse_factor())
        return nodo

    def parse_expresion():
        nodo = parse_producto()
        while siguiente_token() == "+":
            consumir("+")
            nodo = Nodo("+", nodo, parse_producto())
        return nodo

    arbol = parse_expresion()
    if pos[0] != len(tokens):
        raise ValueError("Expresión inválida")
    return arbol
