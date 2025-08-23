from flask import Blueprint, render_template, request, Response
import re
from sympy import symbols, sympify, S
from sympy.logic.boolalg import Or, And, Not, simplify_logic

routes = Blueprint("routes", __name__)

# -------------------- Utilidades de parsing --------------------

def _convert_postfix_not(expr: str) -> str:
    """
    Convierte A' -> ~A y (A+B)' -> ~(A+B).
    También convierte ! a ~. No elimina espacios.
    """
    s = expr
    s = s.replace('·', '*')
    s = s.replace('!', '~')

    # 1) variables con apostrofe: X' -> ~X (repetir hasta que ya no cambie)
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"([A-Za-z]\w*)\s*'", r"~\1", s)

    # 2) grupos con apostrofe: (...)' -> ~(...)
    out = []
    stack = []  # índices en out donde empezó '('
    i = 0
    while i < len(s):
        c = s[i]
        if c == '(':
            stack.append(len(out))
            out.append('(')
            i += 1
        elif c == ')':
            out.append(')')
            # mirar si viene apostrofe después de espacios
            j = i + 1
            while j < len(s) and s[j].isspace():
                j += 1
            if j < len(s) and s[j] == "'":
                if stack:
                    start = stack.pop()
                    group = ''.join(out[start:])
                    out = out[:start] + ['~(', group, ')']
                    i = j + 1
                    continue
            i += 1
        else:
            out.append(c)
            i += 1
    return ''.join(out)

def _normalize_to_sympy_ops(expr: str) -> str:
    """
    + -> |   ;   * -> &   ;   1->True  ; 0->False
    (mantiene ~ para NOT)
    """
    s = expr
    s = re.sub(r"\b1\b", "True", s)
    s = re.sub(r"\b0\b", "False", s)
    s = s.replace('+', '|')
    s = s.replace('*', '&')
    return s

def _extract_vars(expr: str):
    names = set(re.findall(r"[A-Za-z]\w*", expr))
    return sorted([n for n in names if n not in {"True", "False", "Or", "And", "Not"}])

def _pretty(expr) -> str:
    """
    Convierte la expresión SymPy a notación booleana:
    & -> *   | -> +   True->1  False->0  ~A -> A'
    """
    s = str(expr)
    s = s.replace("True", "1").replace("False", "0")
    s = s.replace("&", " * ").replace("|", " + ")

    # convertir negaciones ~A -> A'
    s = re.sub(r"~\s*([A-Za-z0-9()]+)", r"\1'", s)

    return re.sub(r"\s+", " ", s).strip()

# -------------------- Reglas etiquetadas (paso a paso) --------------------

def apply_rules_stepwise(expr):
    """
    Aplica reglas simples con etiquetas para construir una traza de pasos.
    Itera hasta que no haya cambios.
    """
    steps = []
    x = expr
    changed = True

    from sympy import Wild
    A = Wild('A')
    B = Wild('B')

    def _log_change(before, after, ley):
        if before != after:
            steps.append(f"{ley}: { _pretty(before) }  →  { _pretty(after) }")
        return after, before != after

    while changed:
        changed = False
        before_loop = x

        # Doble negación
        x2 = x.replace(Not(Not(A)), A)
        x, did = _log_change(x, x2, "Doble negación ( (X')' = X )")
        changed = changed or did

        # Identidad: A + 0 = A ; A * 1 = A
        def _id_or(e):
            if isinstance(e, Or) and any(arg is S.false for arg in e.args):
                kept = tuple(arg for arg in e.args if arg is not S.false)
                return kept[0] if len(kept) == 1 else Or(*kept)
        x2 = x.replace(lambda e: isinstance(e, Or) and S.false in e.args, _id_or)
        x, did = _log_change(x, x2, "Identidad (A + 0 = A)")
        changed = changed or did

        def _id_and(e):
            if isinstance(e, And) and any(arg is S.true for arg in e.args):
                kept = tuple(arg for arg in e.args if arg is not S.true)
                return kept[0] if len(kept) == 1 else And(*kept)
        x2 = x.replace(lambda e: isinstance(e, And) and S.true in e.args, _id_and)
        x, did = _log_change(x, x2, "Identidad (A * 1 = A)")
        changed = changed or did

        # Dominación
        x2 = x.replace(Or(A, S.true), S.true).replace(Or(S.true, A), S.true)
        x, did = _log_change(x, x2, "Dominación (A + 1 = 1)")
        changed = changed or did

        x2 = x.replace(And(A, S.false), S.false).replace(And(S.false, A), S.false)
        x, did = _log_change(x, x2, "Dominación (A * 0 = 0)")
        changed = changed or did

        # Complemento
        x2 = x.replace(Or(A, Not(A)), S.true).replace(Or(Not(A), A), S.true)
        x, did = _log_change(x, x2, "Complemento (A + A' = 1)")
        changed = changed or did

        x2 = x.replace(And(A, Not(A)), S.false).replace(And(Not(A), A), S.false)
        x, did = _log_change(x, x2, "Complemento (A * A' = 0)")
        changed = changed or did

        # Idempotencia
        x2 = x.replace(Or(A, A), A)
        x, did = _log_change(x, x2, "Idempotencia (A + A = A)")
        changed = changed or did

        x2 = x.replace(And(A, A), A)
        x, did = _log_change(x, x2, "Idempotencia (A * A = A)")
        changed = changed or did

        # Absorción
        x2 = x.replace(Or(A, And(A, B)), A).replace(Or(And(A, B), A), A)
        x, did = _log_change(x, x2, "Absorción (A + A·B = A)")
        changed = changed or did

        x2 = x.replace(And(A, Or(A, B)), A).replace(And(Or(A, B), A), A)
        x, did = _log_change(x, x2, "Absorción (A * (A + B) = A)")
        changed = changed or did

        if x == before_loop:
            break

    return x, steps

def simplify_with_trace(expr):
    """
    Devuelve (resultado_final, pasos[]) con transformaciones etiquetadas + simplificación mínima.
    """
    mid, steps = apply_rules_stepwise(expr)
    final = simplify_logic(mid, force=True)
    if final != mid:
        steps.append(f"Forma mínima (SymPy): { _pretty(mid) }  →  { _pretty(final) }")
    return final, steps

# -------------------- Rutas --------------------

@routes.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    pasos = []

    if request.method == "POST":
        entrada = request.form.get("expresion", "")

        if not entrada.strip():
            return render_template("index.html", resultado=None, pasos=[])

        # 1) Normalizar entrada
        s = _convert_postfix_not(entrada)
        s = _normalize_to_sympy_ops(s)

        # 2) Validar límite de variables
        var_names = _extract_vars(s)
        if len(var_names) > 5:
            pasos = [
                "⚠️ Límite de variables excedido.",
                f"Detectadas: {', '.join(var_names)}",
                "Este plan permite hasta 5 variables. Para más, se requiere suscripción."
            ]
            return render_template("index.html", resultado=None, pasos=pasos)

        # 3) Crear símbolos dinámicos
        locals_map = {}
        if var_names:
            syms = symbols(' '.join(var_names), boolean=True)
            if not isinstance(syms, tuple):
                syms = (syms,)
            locals_map.update(dict(zip(var_names, syms)))

        # 4) Parsear
        try:
            expr = sympify(s, locals=locals_map)
        except Exception as e:
            pasos = [f"❌ Error al interpretar la expresión: {e}"]
            return render_template("index.html", resultado=None, pasos=pasos)

        # 5) Simplificar con pasos
        final_expr, steps = simplify_with_trace(expr)
        resultado = _pretty(final_expr)
        pasos = ["Función ingresada: " + entrada] + steps + [f"Resultado final: {resultado}"]

    return render_template("index.html", resultado=resultado, pasos=pasos)

@routes.route("/reglas")
def reglas():
    return render_template("reglas.html")

@routes.route("/guardar", methods=["POST"])
def guardar():
    pasos = request.form.get("pasos", "")
    contenido = f"Resultado de la simplificación:\n\n{pasos}"
    return Response(
        contenido,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=resultado.txt"}
    )
