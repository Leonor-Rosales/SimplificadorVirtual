class Nodo:
    def __init__(self, valor, izquierda=None, derecha=None):
        self.valor = valor
        self.izquierda = izquierda
        self.derecha = derecha

    def __str__(self):
        if self.valor == "~":
            return f"~({self.izquierda})"
        if self.izquierda and self.derecha:
            return f"({self.izquierda} {self.valor} {self.derecha})"
        return str(self.valor)
