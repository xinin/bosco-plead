import os
import uuid
from prov.model import ProvDocument
from prov.dot import prov_to_dot
import requests
import json


def serialize(document: ProvDocument, name: str):
    """
    Serializa un documento PROV en formato JSON y lo guarda en un archivo.

    Args:
        document (ProvDocument): El documento PROV a serializar.
        name (str): Ruta completa del archivo donde se guardará.
    """
    # Asegurarse de que el directorio exista
    os.makedirs(os.path.dirname(name), exist_ok=True)
    with open(name, "w") as file:
        file.write(document.serialize(format="json"))


def deserialize(file: str) -> ProvDocument:
    """
    Deserializa un archivo en un documento PROV.

    Args:
        file (str): Ruta completa del archivo a deserializar.

    Returns:
        ProvDocument: El documento PROV deserializado.
    """
    path = f"outputs/{file}/provdoc.json"
    with open(path, "r") as f:
        return ProvDocument.deserialize(content=f.read(), format="json")


def draw(document: ProvDocument, name: str):
    """
    Genera un archivo PNG visualizando el documento PROV.

    Args:
        document (ProvDocument): El documento PROV a visualizar.
        name (str): Ruta completa del archivo PNG que se generará.
    """
    # Asegurarse de que el directorio exista
    os.makedirs(os.path.dirname(name), exist_ok=True)
    dot = prov_to_dot(document)
    dot.write_png(name + ".png")


def get_uuid():
    """
    Genera un UUID único.

    Returns:
        str: Un UUID como cadena de texto.
    """
    return str(uuid.uuid4())


def save(provdoc: ProvDocument, _uuid: str, name: str):
    """
    Guarda un documento PROV serializado y genera su visualización en PNG.

    Args:
        provdoc (ProvDocument): El documento PROV a guardar.
        _uuid (str): Identificador único para el directorio de salida.
        name (str): Nombre base del archivo (sin extensión).
    """
    path = f"outputs/{_uuid}"
    serialize(provdoc, f"{path}/provdoc.json")
    draw(provdoc, f"{path}/{name}")


def make_post_request(url, data):
    try:
        # Realizar la solicitud POST, enviando los datos como JSON
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=json.dumps(data), headers=headers)

        # Verificar si la solicitud fue exitosa (código de estado 200)
        if response.status_code == 200:
            return response.json()  # Retorna el contenido de la respuesta como JSON
        else:
            return {
                "error": "Error en la solicitud",
                "status_code": response.status_code,
            }

    except requests.exceptions.RequestException as e:
        # Capturar cualquier error que ocurra durante la solicitud
        return {"error": str(e)}


def save_json(_uuid, data):

    path = f"outputs/{_uuid}/data.json"

    # Obtener la ruta del directorio donde se va a guardar el archivo
    dir = os.path.dirname(path)

    # Si el directorio no existe, lo crea
    if dir and not os.path.exists(dir):
        os.makedirs(dir)

    # Abrir el archivo en modo escritura ('w')
    with open(path, "w", encoding="utf-8") as f:
        # Convertir el diccionario a JSON y escribirlo en el archivo
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_json(_uuid):
    path = f"outputs/{_uuid}/data.json"

    # Verificar si el archivo existe
    if not os.path.exists(path):
        raise FileNotFoundError(f"El archivo {path} no existe.")

    # Abrir el archivo en modo lectura ('r')
    with open(path, "r", encoding="utf-8") as f:
        # Cargar el contenido del archivo JSON
        data = json.load(f)

    return data
