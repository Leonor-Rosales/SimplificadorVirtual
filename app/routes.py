from flask import Blueprint, render_template, request, Response

routes = Blueprint("routes", __name__)

@routes.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    pasos = []

    if request.method == "POST":
        funcion = request.form.get("expresion")  # coincide con el input de index.html

        # 🔹 Aquí pondremos la lógica real después
        pasos = [
            f"Función ingresada: {funcion}",
            "Aplicamos ley de identidad: A + 0 = A",
            "Resultado final: A"
        ]
        resultado = "A"  # resultado final simplificado

    return render_template("index.html", resultado=resultado, pasos=pasos)

@routes.route("/reglas")
def reglas():
    return render_template("reglas.html")

@routes.route("/simplificar", methods=["POST"])
def simplificar():
    funcion = request.form.get("funcion")

    # 🔹 Aquí pondremos la lógica real después
    pasos = [
        f"Función ingresada: {funcion}",
        "Aplicamos ley de identidad: A + 0 = A",
        "Resultado final: A"
    ]

    return render_template("resultado.html", pasos=pasos)

@routes.route("/guardar", methods=["POST"])
def guardar():
    pasos = request.form.get("pasos")

    contenido = f"Resultado de la simplificación:\n\n{pasos}"

    return Response(
        contenido,
        mimetype="text/plain",
        headers={
            "Content-Disposition": "attachment;filename=resultado.txt"
        }
    )
