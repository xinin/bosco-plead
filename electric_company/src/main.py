import os

import redis
from flask import Flask, request, render_template, request, url_for, redirect

from modules.utils import get_uuid

from classes.steps import (
    create_request,
    send_documentation_checked_to_gov,
    check_documentation,
)

# Conexión a Redis
redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)

app = Flask(__name__, template_folder=os.path.join(os.getcwd(), "templates"), static_folder='outputs')


# Página principal con el formulario
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Obtener datos del formulario
        name = request.form.get("name")
        surname = request.form.get("surname")
        dni = request.form.get("dni")
        email = request.form.get("email")

        uuid = get_uuid()
        print("Nueva petición entrante con UUID " + uuid)

        # Crear la petición y guardar los datos de entrada
        create_request(
            uuid, {"name": name, "surname": surname, "dni": dni, "email": email}
        )

        # Comprobar que los datos son correctos
        check_documentation(uuid)

        # Enviar los datos a BOSCO para comprobar si el peticionario puede acceder a o no al BONO SOCIAL
        send_documentation_checked_to_gov(uuid)

        # Redirigir a una página de éxito
        # return render_template("success.html")
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

    # Renderizar el template 'provenance.html' pasando el valor del parámetro
    return render_template("provenance.html", uuid=uuid)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
