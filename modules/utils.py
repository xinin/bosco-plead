import os
import uuid
from prov.model import ProvDocument
from prov.dot import prov_to_dot

@staticmethod
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

@staticmethod
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

@staticmethod
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

@staticmethod
def get_uuid() -> str:
    """
    Genera un UUID único.

    Returns:
        str: Un UUID como cadena de texto.
    """
    return str(uuid.uuid4())

@staticmethod
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