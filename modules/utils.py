import uuid

from prov.model import ProvDocument
from prov.dot import prov_to_dot


@staticmethod
def serialize(document, name):
    with open(name, "w") as file:
        file.write(document.serialize(format="json"))


@staticmethod
def deserialize(file):
    with open(file, "r") as f:
        return ProvDocument.deserialize(content=f.read(), format="json")

@staticmethod
def draw(document, name):
    dot = prov_to_dot(document)
    dot.write_png(name+".png")


@staticmethod
def get_uuid():
    return str(uuid.uuid4())