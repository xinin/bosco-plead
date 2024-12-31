from prov.model import ProvDocument, PROV
from prov.dot import prov_to_dot

d1 = ProvDocument()
nm_requester = d1.add_namespace('requester', 'https://example.org/requester')

# Crear agente y entidad inicial
requester = d1.agent(nm_requester['Requester1'], {"prov:type": "prov:Person"})
documentation = d1.entity(nm_requester['Documentation'], {"prov:label": "Initial Documentation"})
d1.wasAttributedTo(documentation, requester)

# Serializar
with open("prov_step1.json", "w") as file:
    file.write(d1.serialize(format='json'))


# Deserializar
with open("prov_step1.json", "r") as file:
    d1 = ProvDocument.deserialize(content=file.read(), format='json')

# Añadir actividades y agentes
nm_ec = d1.add_namespace('ec', 'https://example.org/electric_company')
electric_company = d1.agent(nm_ec['ElectricCompany'], {"prov:type": "prov:Organization"})
check_documentation = d1.activity(nm_ec['CheckDocumentation'])
check_documentation.add_attributes({"prov:label": "Check Documentation"})

d1.wasAssociatedWith(check_documentation, electric_company)
d1.used(check_documentation, d1.get_record(nm_requester['Documentation'])[0])

# Serializar
with open("prov_step2.json", "w") as file:
    file.write(d1.serialize(format='json'))


# Deserializar
with open("prov_step2.json", "r") as file:
    d1 = ProvDocument.deserialize(content=file.read(), format='json')

# Añadir actividades del gobierno
nm_gov = d1.add_namespace('gov', 'https://example.org/government')
gov = d1.agent(nm_gov['Government'], {"prov:type": "prov:Organization"})
validate_docs = d1.activity(nm_gov['ValidateDocs'])
validate_docs.add_attributes({"prov:label": "Validate Documentation"})

d1.wasAssociatedWith(validate_docs, gov)
d1.used(validate_docs, d1.get_record(nm_requester['Documentation'])[0])

validation_result = d1.entity(nm_gov['ValidationResult'], {"prov:label": "Validation Result"})
d1.wasGeneratedBy(validation_result, validate_docs)

# Serializar
with open("prov_step3.json", "w") as file:
    file.write(d1.serialize(format='json'))


# Deserializar
with open("prov_step3.json", "r") as file:
    final = ProvDocument.deserialize(content=file.read(), format='json')
    # Exportar como imagen
    dot = prov_to_dot(final)
    dot.write_png('workflow-pasos.png')