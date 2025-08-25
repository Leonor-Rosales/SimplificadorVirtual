from flask import Blueprint, render_template, request, Response
from .logic.arbol import construir_arbol
from .logic.simplificador import simplificar_arbol

historial_expresiones = []
routes = Blueprint("routes", __name__)
@routes.route("/", methods=["GET", "POST"])
def index():
    funcion_original = ""
    pasos_detallados = []
    resultado = ""
    pasos_txt = ""

    if request.method == "POST":
        funcion_original = request.form.get("expresion", "")

        # 🔹 Guardar en historial si no está repetida
        if funcion_original and funcion_original not in historial_expresiones:
            historial_expresiones.insert(0, funcion_original)  # insertar al inicio
            if len(historial_expresiones) > 10:  # máximo 10 expresiones
                historial_expresiones.pop()

        # 🔹 Lógica de simplificación (tu función actual)
        arbol = construir_arbol(funcion_original)
        arbol_simplificado, pasos_detallados = simplificar_arbol(arbol)
        resultado = str(arbol_simplificado)

        # 🔹 Pasos en texto plano para guardar en txt
        pasos_txt = "\n".join([f"Paso {i+1}: {p['antes']} → {p['despues']} ({p['ley']})"
                               for i, p in enumerate(pasos_detallados)])

    return render_template(
        "index.html",
        funcion_original=funcion_original,
        pasos_detallados=pasos_detallados,
        resultado=resultado,
        pasos_txt=pasos_txt,
        historial=historial_expresiones
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
