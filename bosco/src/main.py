import json
import time
import threading

import redis
from flask import Flask, request, jsonify

from classes.steps import (
    bosco_ask_information_to_tax_office,
    bosco_cross_data,
    bosco_make_decision,
    bosco_preprocess_documentation,
    send_decision_to_ec,
)

def process_task(task):
    """Procesa la tarea (simulación de trabajo)."""
    uuid = task.get("uuid")
    print(f"Procesando tarea: {uuid}")
    time.sleep(2)  # Simula que está trabajando en la tarea por 2 segundos
    bosco_preprocess_documentation(uuid)
    time.sleep(2)  # Simula que está trabajando en la tarea por 2 segundos
    bosco_ask_information_to_tax_office(uuid)
    time.sleep(2)  # Simula que está trabajando en la tarea por 2 segundos
    bosco_cross_data(uuid)
    time.sleep(2)  # Simula que está trabajando en la tarea por 2 segundos
    bosco_make_decision(uuid)
    time.sleep(2)  # Simula que está trabajando en la tarea por 2 segundos
    send_decision_to_ec(uuid)
    print(f"Tarea {task} procesada.")

def worker():
    """Worker que espera y procesa mensajes de la cola de Redis."""
    # Conexión al servidor Redis
    client = redis.StrictRedis(host="redis", port=6379, db=0)

    # Nombre de la cola en Redis
    queue_name = "task_queue"

    print(f"Esperando tareas en la cola '{queue_name}'...")

    while True:
        # BLPOP bloquea el worker hasta que haya un mensaje en la cola
        task = client.blpop(
            queue_name, timeout=0
        )  # timeout=0 significa espera infinita
        if task:
            # El mensaje es una tupla: (clave, valor)
            task_data = task[1].decode("utf-8")  # Decodificar de bytes a string
            process_task(json.loads(task_data))
        else:
            print("No se recibió tarea.")


app = Flask(__name__)

# Conexión a Redis
redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)

# Endpoint POST que recibe datos JSON y los devuelve
@app.route("/api/data", methods=["POST"])
def handle_data():
    # Obtener los datos JSON del cuerpo de la solicitud
    data = request.get_json()

    # Verificar que los datos sean válidos
    if not data:
        return jsonify({"error": "No se enviaron datos JSON"}), 400

    uuid = data.get("uuid")
    if not uuid:
        return jsonify({"error": "No se enviaron UUID"}), 400

    # Enviar mensaje a la cola de Redis
    redis_client.lpush(
        "task_queue", json.dumps(data)
    )  # 'task_queue' es el nombre de la cola
    print("Peticion con UUID: " + uuid + " añadida a la cola de trabajo.")

    return jsonify({"message": "Datos recibidos con éxito", "data": data}), 200

if __name__ == "__main__":
    # Iniciar el worker en un hilo
    worker_thread = threading.Thread(target=worker)
    worker_thread.daemon = (
        True  # Para que el hilo termine cuando el programa principal termine
    )
    worker_thread.start()

    # Iniciar el servidor Flask
    app.run(host="0.0.0.0", port=8081, debug=True)
