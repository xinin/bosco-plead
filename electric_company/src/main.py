import os

import redis
from flask import Flask, request, render_template, request, url_for, redirect, jsonify

from modules.utils import get_uuid, load_json

from modules.constants import Constants

from classes.steps import (
    create_request,
    send_documentation_checked_to_gov,
    check_documentation,
    send_decision_to_requester,
)

# Conexión a Redis
redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)

app = Flask(
    __name__,
    template_folder=os.path.join(os.getcwd(), "templates"),
    static_folder="outputs",
)


# Página principal con el formulario
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Obtener datos del formulario
        name = request.form.get("name")
        surname = request.form.get("surname")
        dni = request.form.get("dni")
        email = request.form.get("email")

        # Generate UUID for the request
        uuid = get_uuid()
        print("UUID", uuid)

        # Crear la petición y guardar los datos de entrada
        if not create_request(
            uuid,
            {
                "name": name,
                "surname": surname,
                "dni": dni,
                "email": email,
                "status": Constants.REQUEST_STATUS_PENDING,
            },
        ):
            return redirect(url_for("success", uuid=uuid))

        # Comprobar que los datos son correctos
        if not check_documentation(uuid):
            return redirect(url_for("success", uuid=uuid))

        # Enviar los datos a BOSCO para comprobar si el peticionario puede acceder al BONO SOCIAL
        send_documentation_checked_to_gov(uuid)

        # Redirigir a una página de éxito
        return redirect(url_for("success", uuid=uuid))

    return render_template("index.html")


@app.route("/success")
def success():
    # Obtener el parámetro de la query string 'mensaje'
    uuid = request.args.get("uuid")

    # Renderizar el template 'success.html' pasando el valor del parámetro
    return render_template("success.html", uuid=uuid)


@app.route("/provenance")
def provenance():
    # Obtener el parámetro de la query string 'uuid'
    uuid = request.args.get("uuid")

    # Cargar los datos desde el archivo JSON utilizando el uuid
    data = load_json(uuid)

    # Lista de pasos con sus imágenes
    steps = [
        {"step": 1, "name": "send_request"},
        {"step": 2, "name": "check_documentation"},
        {"step": 3, "name": "send_documentation_checked_to_gov"},
        {"step": 4, "name": "bosco_preprocess_documentation"},
        {"step": 5, "name": "bosco_ask_tax_info"},
        {"step": 6, "name": "data_crossed"},
        {"step": 7, "name": "make_decision"},
        {"step": 8, "name": "send_decision_to_ec"},
        {"step": 9, "name": "send_decision_to_requester"},
    ]

    # Comprobar si la imagen existe para cada paso
    for step in steps:
        image_path = f"outputs/{uuid}/{step['step']}_{step['name']}.png"
        step["exists"] = os.path.exists(image_path)

    # Renderizar el template 'provenance.html' pasando los datos necesarios
    return render_template("provenance.html", uuid=uuid, data=data, steps=steps)


# Endpoint POST que recibe datos JSON y los devuelve
@app.route("/api/decision", methods=["POST"])
def handle_data():
    # Obtener los datos JSON del cuerpo de la solicitud
    data = request.get_json()

    # Verificar que los datos sean válidos
    if not data:
        return jsonify({"error": "No se enviaron datos JSON"}), 400

    uuid = data.get("uuid")
    if not uuid:
        return jsonify({"error": "No se enviaron UUID"}), 400

    send_decision_to_requester(uuid)

    return jsonify({"message": "Datos recibidos con éxito"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
