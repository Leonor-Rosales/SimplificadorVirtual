from flask import Blueprint, render_template, request, redirect, url_for, Response
from .logic.arbol import construir_arbol, validar_expresion
from .logic.nodo import Nodo
from .logic.simplificador import simplificar_arbol
import re

routes = Blueprint("routes", __name__)
historial_expresiones = []

def normalizar_expresion(expresion):
    """
    Convierte expresiones como AB o A1 en A*B o A*1 automáticamente.
    """
    expr = expresion.replace(" ", "")
    # Agrega * entre: letra seguida de letra o número
    expr = re.sub(r"([A-Z0-1])(?=[A-Z0-1])", r"\1*", expr)
    return expr

@routes.route("/", methods=["GET", "POST"])
def index():
    funcion_original = ""
    pasos_detallados = []
    resultado = ""
    pasos_txt = ""
    error = None

    if request.method == "POST":
        funcion_original = request.form.get("expresion", "").strip()
        # Normalizar la expresión
        funcion_normalizada = normalizar_expresion(funcion_original)

        # Validación
        error = validar_expresion(funcion_normalizada)
        if not error:
            try:
                arbol = construir_arbol(funcion_normalizada)
                arbol_final, pasos_detallados = simplificar_arbol(arbol)
                resultado = str(arbol_final)
                pasos_txt = "\n".join([f"{p['antes']} -> {p['despues']} ({p['ley']})" for p in pasos_detallados])
                if funcion_original not in historial_expresiones:
                    historial_expresiones.append(funcion_original)
            except Exception as e:
                error = f"Error al procesar la expresión: {str(e)}"

    return render_template(
        "index.html",
        funcion_original=funcion_original,
        pasos_detallados=pasos_detallados,
        resultado=resultado,
        pasos_txt=pasos_txt,
        historial=historial_expresiones,
        error=error
    )

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

@routes.route("/variables")
def variables():
    return render_template("variables.html")
