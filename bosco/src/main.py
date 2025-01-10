from classes.provenance import Provenance

from modules.constants import Constants
from modules.utils import deserialize, save
import redis
import json
import time

from flask import Flask, request, jsonify
import threading


def bosco_preprocess_documentation(uuid):
    # Get ProvDoc
    provdoc = deserialize(uuid)

    # Get Namespace EC
    nm_ec = Provenance.get_namespace_by_id(provdoc, Constants.NM_EC["prefix"])

    # Get Namespace Gov and agent BOSCO
    nm_gov = Provenance.get_namespace_by_id(provdoc, Constants.NM_GOV["prefix"])
    bosco = Provenance.get_agent_by_id(provdoc, nm_gov[Constants.AGENT_ID_BOSCO])
    
    # Get Documentation entity
    documentation_checked = Provenance.get_entity_by_id(provdoc, nm_ec['DocumentationChecked'])

    # Get Activity Send to EC
    send_to_gov = Provenance.get_activity_by_id(provdoc, nm_ec['SendToGov'])

    # BOSCO preprocess documentation
    preprocess_documentation = Provenance.create_activity(provdoc, nm_gov['PreprocessDocumentation'],"Preprocess Documentation by BOSCO" )    
    Provenance.wasAssociatedWith(provdoc, preprocess_documentation, bosco)
    Provenance.wasInformedBy(provdoc, preprocess_documentation, send_to_gov)
    Provenance.used(provdoc, preprocess_documentation, documentation_checked)
    Provenance.wasAssociatedWith(provdoc, preprocess_documentation, bosco)

    save(provdoc, uuid,"4_bosco_preprocess_documentation" )

def bosco_ask_information_to_tax_office(uuid):
     # Get ProvDoc
    provdoc = deserialize(uuid)

    # Get Namespace Gov and agent BOSCO
    nm_gov = Provenance.get_namespace_by_id(provdoc, Constants.NM_GOV["prefix"])
    bosco = Provenance.get_agent_by_id(provdoc, nm_gov[Constants.AGENT_ID_BOSCO])
    
    # Get Activity Send to EC
    preprocess_documentation = Provenance.get_activity_by_id(provdoc, nm_gov['PreprocessDocumentation'])

    # Create Agent Tax Office
    tax_office = Provenance.create_agent(provdoc, nm_gov[Constants.AGENT_ID_TAX_OFFICE], Constants.AGENT_TYPE_ORGANIZATION, 'TAX OFFICE')

    # BOSCO ask information from the Tax Office
    retrieve_tax_info = Provenance.create_activity(provdoc, nm_gov['RetrieveTaxInfo'],"Retrieves Tax Info" )    
    Provenance.wasAssociatedWith(provdoc, retrieve_tax_info, tax_office)
    Provenance.wasAssociatedWith(provdoc, retrieve_tax_info, bosco)
    Provenance.wasInformedBy(provdoc, retrieve_tax_info, preprocess_documentation)
    Provenance.wasAssociatedWith(provdoc, retrieve_tax_info, tax_office)

    # Create entity TAX INFO
    tax_info = Provenance.create_entity(provdoc, nm_gov['TaxInfo'], 'Tax Information')
    Provenance.wasAttributedTo(provdoc, tax_info, tax_office)
    Provenance.wasGeneratedBy(provdoc, tax_info, retrieve_tax_info)

    save(provdoc, uuid,"5_bosco_ask_tax_info" )

def bosco_cross_data(uuid):
    # Get ProvDoc
    provdoc = deserialize(uuid)

    # Get Namespace EC
    nm_ec = Provenance.get_namespace_by_id(provdoc, Constants.NM_EC["prefix"])

    # Get Namespace Gov and agent BOSCO
    nm_gov = Provenance.get_namespace_by_id(provdoc, Constants.NM_GOV["prefix"])
    bosco = Provenance.get_agent_by_id(provdoc, nm_gov[Constants.AGENT_ID_BOSCO])

    # Get Documentation entity
    documentation_checked = Provenance.get_entity_by_id(provdoc, nm_ec['DocumentationChecked'])
    
    # Get Tax Info
    tax_info = Provenance.get_entity_by_id(provdoc, nm_gov['TaxInfo'])

    # Get Activity RetrieveTaxInfo
    retrieve_tax_info = Provenance.get_activity_by_id(provdoc, nm_gov['RetrieveTaxInfo'])

    # Create Activity Cross Data
    cross_data = Provenance.create_activity(provdoc, nm_gov['CrossData'],"Cross Data Info" )   
    Provenance.wasAssociatedWith(provdoc, cross_data, bosco)
    Provenance.wasInformedBy(provdoc, cross_data, retrieve_tax_info)

    # create entity Data Crossed
    data_crossed = Provenance.create_entity(provdoc, nm_gov['DataCrossed'], 'Data Crossed')
    Provenance.wasAttributedTo(provdoc, data_crossed, bosco)
    Provenance.wasGeneratedBy(provdoc, data_crossed, cross_data)
    Provenance.used(provdoc, data_crossed, tax_info)
    Provenance.used(provdoc, data_crossed, documentation_checked)
    Provenance.wasDerivedFrom(provdoc, data_crossed, tax_info)
    Provenance.wasDerivedFrom(provdoc, data_crossed, documentation_checked)

    save(provdoc, uuid,"6_data_crossed" )

def bosco_make_decision(uuid):
    # Get ProvDoc
    provdoc = deserialize(uuid)

    # Get Namespace Gov and agent BOSCO
    nm_gov = Provenance.get_namespace_by_id(provdoc, Constants.NM_GOV["prefix"])
    bosco = Provenance.get_agent_by_id(provdoc, nm_gov[Constants.AGENT_ID_BOSCO])

    # Get Activity CrossData
    cross_data = Provenance.get_activity_by_id(provdoc, nm_gov['CrossData'])
    
    # Get Data Crossed entity
    data_crossed = Provenance.get_entity_by_id(provdoc, nm_gov['DataCrossed'])

    # Create Activity Make a Decision
    make_decision = Provenance.create_activity(provdoc, nm_gov['MakeDecision'],"Make a Decision")   
    Provenance.wasAssociatedWith(provdoc, make_decision, bosco)
    Provenance.wasInformedBy(provdoc, make_decision, cross_data)

    # Create entity Decision
    decision = Provenance.create_entity(provdoc, nm_gov['Decision'], 'Decision')
    Provenance.wasAttributedTo(provdoc, decision, bosco)
    Provenance.wasGeneratedBy(provdoc, decision, make_decision)
    Provenance.used(provdoc, make_decision, data_crossed)
    Provenance.wasDerivedFrom(provdoc, decision, data_crossed)

    save(provdoc, uuid,"7_make_decision" )

def send_decision_to_ec(uuid):
    # Get ProvDoc
    provdoc = deserialize(uuid)

    # Get Namespace Gov and agent BOSCO
    nm_gov = Provenance.get_namespace_by_id(provdoc, Constants.NM_GOV["prefix"])
    bosco = Provenance.get_agent_by_id(provdoc, nm_gov[Constants.AGENT_ID_BOSCO])

    # Get Namespace and agent Electric Company
    nm_ec = Provenance.get_namespace_by_id(provdoc, Constants.NM_EC["prefix"])
    electric_company = Provenance.get_agent_by_id(provdoc, nm_ec[Constants.AGENT_ID_EC])
    
    # Get Decision entity
    decision = Provenance.get_entity_by_id(provdoc, nm_gov['Decision'])

    # Get MakeDecision
    make_decision = Provenance.get_activity_by_id(provdoc, nm_gov['MakeDecision'])

    # BOSCO send decision to EC
    send_decision_to_ec = Provenance.create_activity(provdoc, nm_gov['SendDecision'],"Send the Decision to EC")   
    Provenance.wasAssociatedWith(provdoc, send_decision_to_ec, bosco)
    Provenance.wasAssociatedWith(provdoc, send_decision_to_ec, electric_company)
    Provenance.used(provdoc, send_decision_to_ec, decision)
    Provenance.wasInformedBy(provdoc, send_decision_to_ec, make_decision)

    save(provdoc, uuid,"8_send_decision_to_ec" )

def process_task(task):
    """Procesa la tarea (simulación de trabajo)."""
    uuid = task.get("uuid")
    print(f"Procesando tarea: {uuid}")
    time.sleep(2)  # Simula que está trabajando en la tarea por 2 segundos
    bosco_preprocess_documentation(uuid)
    bosco_ask_information_to_tax_office(uuid)
    bosco_cross_data(uuid)
    bosco_make_decision(uuid)
    send_decision_to_ec(uuid)
    print(f"Tarea {task} completada..")




def worker():
    """Worker que espera y procesa mensajes de la cola de Redis."""
    # Conexión al servidor Redis
    client = redis.StrictRedis(host='redis', port=6379, db=0)

    # Nombre de la cola en Redis
    queue_name = "task_queue"

    print(f"Esperando tareas en la cola '{queue_name}'...")

    while True:
        # BLPOP bloquea el worker hasta que haya un mensaje en la cola
        task = client.blpop(queue_name, timeout=0)  # timeout=0 significa espera infinita
        if task:
            # El mensaje es una tupla: (clave, valor)
            task_data = task[1].decode("utf-8")  # Decodificar de bytes a string
            process_task(task_data)
        else:
            print("No se recibió tarea.")

app = Flask(__name__)

# Conexión a Redis
redis_client = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=True)

# Endpoint POST que recibe datos JSON y los devuelve
@app.route('/api/data', methods=['POST'])
def handle_data():
    # Obtener los datos JSON del cuerpo de la solicitud
    print("LLEGA LA PETICION")
    
    data = request.get_json()
    
    # Verificar que los datos sean válidos
    if not data:
        return jsonify({"error": "No se enviaron datos JSON"}), 400
    
    uuid = data.get("uuid")
    if not uuid:
        return jsonify({"error": "No se enviaron UUID"}), 400
    
    print("#################")
    print("ID: "+uuid)

    # Enviar mensaje a la cola de Redis
    redis_client.lpush('task_queue', json.dumps(data))  # 'task_queue' es el nombre de la cola

    return jsonify({"message": "Datos recibidos con éxito", "data": data}), 200

if __name__ == '__main__':
    # Iniciar el worker en un hilo
    worker_thread = threading.Thread(target=worker)
    worker_thread.daemon = True  # Para que el hilo termine cuando el programa principal termine
    worker_thread.start()

    # Iniciar el servidor Flask
    app.run(host='0.0.0.0', port=8081, debug=True)
