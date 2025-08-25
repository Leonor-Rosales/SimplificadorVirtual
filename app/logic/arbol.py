from .nodo import Nodo

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
