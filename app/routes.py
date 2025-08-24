from flask import Blueprint, render_template, request, Response
import re
from sympy import symbols, sympify, S
from sympy.logic.boolalg import Or, And, Not, simplify_logic
from .reglas import simplificar_expresion

routes = Blueprint("routes", __name__)

# -------------------- Utilidades --------------------

def _convert_postfix_not(expr: str) -> str:
    s = expr.replace('·', '*').replace('!', '~')
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"([A-Za-z]\w*)\s*'", r"~\1", s)

    out, stack, i = [], [], 0
    while i < len(s):
        c = s[i]
        if c == '(':
            stack.append(len(out))
            out.append('(')
            i += 1
        elif c == ')':
            out.append(')')
            j = i + 1
            while j < len(s) and s[j].isspace(): j += 1
            if j < len(s) and s[j] == "'" and stack:
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
    s = expr
    s = re.sub(r"\b1\b", "True", s)
    s = re.sub(r"\b0\b", "False", s)
    s = s.replace('+', '|').replace('*', '&')
    return s

def _extract_vars(expr: str):
    names = set(re.findall(r"[A-Za-z]\w*", expr))
    return sorted([n for n in names if n not in {"True", "False", "Or", "And", "Not"}])

def _fmt_expr(e) -> str:
    from sympy import Symbol
    from sympy.logic.boolalg import BooleanTrue, BooleanFalse
    if e is S.true or isinstance(e, BooleanTrue): return "1"
    if e is S.false or isinstance(e, BooleanFalse): return "0"
    if isinstance(e, Symbol): return str(e)
    if isinstance(e, Not):
        inner = e.args[0]
        inner_s = _fmt_expr(inner)
        return f"({inner_s})'" if isinstance(inner, (Or, And)) else f"{inner_s}'"
    if isinstance(e, Or): return " + ".join([_fmt_expr(a) for a in e.args])
    if isinstance(e, And):
        parts = []
        for a in e.args:
            s = _fmt_expr(a)
            if isinstance(a, Or): s = f"({s})"
            parts.append(s)
        return " * ".join(parts)
    return str(e)

def _pretty(expr) -> str:
    return _fmt_expr(expr)

# -------------------- Reglas paso a paso --------------------

def apply_rules_stepwise(expr):
    from sympy import Wild
    A, B = Wild('A'), Wild('B')
    steps = []
    x = expr
    changed = True

    def _push_step(before, after, ley):
        if before != after:
            steps.append({"ley": ley, "antes": _pretty(before), "despues": _pretty(after)})
        return after, before != after

    while changed:
        changed = False
        before_loop = x

        # Doble negación
        x2 = x.replace(Not(Not(A)), A)
        x, did = _push_step(x, x2, "Doble negación")
        changed = changed or did

        # Identidad A + 0 = A
        def _id_or(e):
            if isinstance(e, Or) and any(arg is S.false for arg in e.args):
                kept = tuple(arg for arg in e.args if arg is not S.false)
                return kept[0] if len(kept) == 1 else Or(*kept)
        x2 = x.replace(lambda e: isinstance(e, Or) and S.false in e.args, _id_or)
        x, did = _push_step(x, x2, "Identidad A + 0 = A")
        changed = changed or did

        # Identidad A * 1 = A
        def _id_and(e):
            if isinstance(e, And) and any(arg is S.true for arg in e.args):
                kept = tuple(arg for arg in e.args if arg is not S.true)
                return kept[0] if len(kept) == 1 else And(*kept)
        x2 = x.replace(lambda e: isinstance(e, And) and S.true in e.args, _id_and)
        x, did = _push_step(x, x2, "Identidad A * 1 = A")
        changed = changed or did

        # Dominación
        x2 = x.replace(Or(A, S.true), S.true).replace(Or(S.true, A), S.true)
        x, did = _push_step(x, x2, "Dominación A + 1 = 1")
        changed = changed or did
        x2 = x.replace(And(A, S.false), S.false).replace(And(S.false, A), S.false)
        x, did = _push_step(x, x2, "Dominación A * 0 = 0")
        changed = changed or did

        # Complemento
        x2 = x.replace(Or(A, Not(A)), S.true).replace(Or(Not(A), A), S.true)
        x, did = _push_step(x, x2, "Complemento A + A' = 1")
        changed = changed or did
        x2 = x.replace(And(A, Not(A)), S.false).replace(And(Not(A), A), S.false)
        x, did = _push_step(x, x2, "Complemento A * A' = 0")
        changed = changed or did

        # Idempotencia
        x2 = x.replace(Or(A, A), A)
        x, did = _push_step(x, x2, "Idempotencia A + A = A")
        changed = changed or did
        x2 = x.replace(And(A, A), A)
        x, did = _push_step(x, x2, "Idempotencia A * A = A")
        changed = changed or did

        # Absorción
        x2 = x.replace(Or(A, And(A, B)), A).replace(Or(And(A, B), A), A)
        x, did = _push_step(x, x2, "Absorción A + A·B = A")
        changed = changed or did
        x2 = x.replace(And(A, Or(A, B)), A).replace(And(Or(A, B), A), A)
        x, did = _push_step(x, x2, "Absorción A * (A + B) = A")
        changed = changed or did

        if x == before_loop: break

    return x, steps

def simplify_with_trace(expr):
    mid, steps = apply_rules_stepwise(expr)
    final = simplify_logic(mid, force=True)
    if final != mid:
        steps.append({"ley": "Forma mínima (SymPy)", "antes": _pretty(mid), "despues": _pretty(final)})
    return final, steps

# -------------------- Rutas --------------------

@routes.route("/", methods=["GET", "POST"])
def index():
    funcion_original = None
    pasos_detallados = []
    resultado = None
    pasos_txt = ""
    subs_requerida = False
    mensaje_subs = ""

    if request.method == "POST":
        entrada = request.form.get("expresion", "").strip()
        funcion_original = entrada

        if not entrada:
            return render_template("index.html", funcion_original=None, pasos_detallados=[], resultado=None,
                                   subs_requerida=False, mensaje_subs="", pasos_txt="")

        s = _convert_postfix_not(entrada)
        s = _normalize_to_sympy_ops(s)

        var_names = _extract_vars(s)
        if len(var_names) > 5:
            subs_requerida = True
            mensaje_subs = f"Detectadas {len(var_names)} variables: {', '.join(var_names)}. Para más de 5 variables se requiere suscripción."
            return render_template("index.html", funcion_original=funcion_original,
                                   pasos_detallados=[], resultado=None,
                                   subs_requerida=subs_requerida, mensaje_subs=mensaje_subs,
                                   pasos_txt="")

        locals_map = {}
        if var_names:
            syms = symbols(' '.join(var_names), boolean=True)
            if not isinstance(syms, tuple):
                syms = (syms,)
            locals_map.update(dict(zip(var_names, syms)))

        try:
            expr = sympify(s, locals=locals_map)
        except Exception as e:
            pasos_detallados = [f"Error de sintaxis: {e}"]
            return render_template("index.html", funcion_original=funcion_original,
                                   pasos_detallados=pasos_detallados, resultado=None,
                                   subs_requerida=False, mensaje_subs="", pasos_txt="")

        final_expr, pasos = simplify_with_trace(expr)

        # PASAR LOS DICCIONARIOS DIRECTAMENTE AL TEMPLATE
        pasos_detallados = pasos
        pasos_txt = "\n".join([f"{p['ley']}: {p['antes']} → {p['despues']}" for p in pasos])
        resultado = _pretty(final_expr)

    return render_template("index.html",
                           funcion_original=funcion_original,
                           pasos_detallados=pasos_detallados,
                           resultado=resultado,
                           subs_requerida=subs_requerida,
                           mensaje_subs=mensaje_subs,
                           pasos_txt=pasos_txt)




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

@routes.route("/simplificar", methods=["POST"])
def simplificar():
    funcion = request.form.get("funcion")

    pasos = simplificar_expresion(funcion)

    return render_template("resultado.html", pasos=pasos)

