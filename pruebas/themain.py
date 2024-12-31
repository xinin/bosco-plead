from prov.model import ProvDocument, PROV
from prov.dot import prov_to_dot

# Crear el documento PROV
d1 = ProvDocument()

# Namespaces
nm_requester = d1.add_namespace('requester', 'https://dictionary.cambridge.org/es/diccionario/ingles/requester')
nm_ec = d1.add_namespace('ec', 'https://en.wikipedia.org/wiki/The_Electric_Company')
nm_gov = d1.add_namespace('gov', 'https://en.wikipedia.org/wiki/Government')
nm_bosco = d1.add_namespace('bosco', 'https://example.org/BOSCO')
nm_tax = d1.add_namespace('tax', 'https://example.org/Hacienda')

# AGENTES
# Peticionario
requester = d1.agent(nm_requester['Requester1'], {"prov:type": PROV["Person"], "prov:label": "Requester 1"})
# Compañía Eléctrica
electric_company = d1.agent(nm_ec['ElectricCompany'], {"prov:type": PROV["Organization"], "prov:label": "Electric Company"})
# Gobierno
gov = d1.agent(nm_gov['Government'], {"prov:type": PROV["Organization"], "prov:label": "Government"})
# BOSCO
bosco = d1.agent(nm_bosco['BOSCO'], {"prov:type": PROV["SoftwareAgent"], "prov:label": "BOSCO System"})
# Hacienda
hacienda = d1.agent(nm_tax['Hacienda'], {"prov:type": PROV["Organization"], "prov:label": "Hacienda"})

# ENTIDADES
# Documentación enviada por el peticionario
documentation = d1.entity(nm_requester['Documentation'], {"prov:label": "Documentation"})
# Resultado de la validación por parte del gobierno
validation_result = d1.entity(nm_gov['ValidationResult'], {"prov:label": "Validation Result"})
# Datos cruzados por BOSCO
crossed_data = d1.entity(nm_bosco['CrossedData'], {"prov:label": "Crossed Data with Tax System"})

# ACTIVIDADES
# Peticionario envía la documentación a la compañía eléctrica
send_to_ec = d1.activity(nm_requester['SendToEC'])
send_to_ec.add_attributes({"prov:label": "Send Documentation to Electric Company"})
d1.wasAssociatedWith(send_to_ec, requester)
d1.used(send_to_ec, documentation)
d1.wasGeneratedBy(documentation, send_to_ec)

# Compañía Eléctrica revisa la documentación
check_documentation = d1.activity(nm_ec['CheckDocumentation'])
check_documentation.add_attributes({"prov:label": "Check Documentation"})
d1.wasAssociatedWith(check_documentation, electric_company)
d1.wasInformedBy(check_documentation, send_to_ec)

# Compañía Eléctrica envía la documentación al gobierno
send_to_gov = d1.activity(nm_ec['SendToGov'])
send_to_gov.add_attributes({"prov:label": "Send Documentation to Government"})
d1.wasAssociatedWith(send_to_gov, electric_company)
d1.wasInformedBy(send_to_gov, check_documentation)

# Gobierno valida la documentación
validate_docs = d1.activity(nm_gov['ValidateDocs'])
validate_docs.add_attributes({"prov:label": "Validate Documentation"})
d1.wasAssociatedWith(validate_docs, gov)
d1.wasInformedBy(validate_docs, send_to_gov)
d1.used(validate_docs, documentation)

# BOSCO cruza los datos con Hacienda
cross_data = d1.activity(nm_bosco['CrossData'])
cross_data.add_attributes({"prov:label": "Cross Data with Tax System"})
d1.wasAssociatedWith(cross_data, bosco)
d1.used(cross_data, documentation)
d1.used(cross_data, hacienda)
d1.wasGeneratedBy(crossed_data, cross_data)

# Relacionar BOSCO y Hacienda con el gobierno
d1.wasAttributedTo(crossed_data, bosco)
d1.wasDerivedFrom(crossed_data, documentation)
d1.wasDerivedFrom(crossed_data, hacienda)

# Resultado final basado en los datos cruzados
d1.wasGeneratedBy(validation_result, validate_docs)
d1.wasDerivedFrom(validation_result, crossed_data)

# Gobierno envía el resultado de la validación a la compañía eléctrica
send_result_to_ec = d1.activity(nm_gov['SendResultToEC'])
send_result_to_ec.add_attributes({"prov:label": "Send Validation Result to Electric Company"})
d1.wasAssociatedWith(send_result_to_ec, gov)
d1.used(send_result_to_ec, validation_result)
d1.wasInformedBy(send_result_to_ec, validate_docs)

# Compañía Eléctrica envía el resultado al peticionario
send_result_to_requester = d1.activity(nm_ec['SendResultToRequester'])
send_result_to_requester.add_attributes({"prov:label": "Send Result to Requester"})
d1.wasAssociatedWith(send_result_to_requester, electric_company)
d1.used(send_result_to_requester, validation_result)
d1.wasInformedBy(send_result_to_requester, send_result_to_ec)

# RELACIONES FINALES
# Relacionar el resultado con el peticionario
d1.wasAttributedTo(validation_result, gov)
d1.wasDerivedFrom(validation_result, documentation)

# Exportar como imagen
dot = prov_to_dot(d1)
dot.write_png('workflow-prov-extended.png')
