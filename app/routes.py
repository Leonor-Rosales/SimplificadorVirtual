from flask import Blueprint, render_template, request
from .logic.simplificador import simplificar

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    pasos = []

    if request.method == "POST":
        expresion = request.form.get("expresion")
        resultado, pasos = simplificar(expresion)

    return render_template("index.html", resultado=resultado, pasos=pasos)

@main.route("/reglas")
def reglas():
    return render_template("reglas.html")
