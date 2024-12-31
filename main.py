from classes.provenance import Provenance

from modules.constants import NM_REQUESTER,NM_EC, AGENT_TYPE_PERSON, AGENT_TYPE_ORGANIZATION
from modules.utils import serialize, deserialize, draw, get_uuid


def send_request(uuid):
    # Create Provenance Document
    provdoc = Provenance.init_document()

    # Create Namespace de Requester and Eletric Company
    nm_requester = Provenance.create_namespace(provdoc, NM_REQUESTER["prefix"],NM_REQUESTER["uri"])
    nm_ec = Provenance.create_namespace(provdoc, NM_EC["prefix"],NM_EC["uri"])
    
    # Create Agent Requester and Eletric Company
    requester = Provenance.create_agent(provdoc, nm_requester['Requester'], AGENT_TYPE_PERSON, '11111111A')
    electric_company = Provenance.create_agent(provdoc, nm_ec['EC'], AGENT_TYPE_ORGANIZATION, 'Power Supply Gmbh')

    # Create entity Initial Documentation
    documentation = Provenance.create_entity(provdoc, nm_requester['Documentation'], 'Initial Documentation')
    Provenance.wasAttributedTo(provdoc, documentation, requester)

    # Create Activity "Send Documentation to Electric Company"
    send_to_ec = Provenance.create_activity(provdoc, nm_requester['SendToEC'], "Send Documentation to Electric Company")
    Provenance.wasAssociatedWith(provdoc, send_to_ec, requester)
    Provenance.used(provdoc, send_to_ec, documentation)
    Provenance.wasGeneratedBy(provdoc, documentation, send_to_ec)

      
    serialize(provdoc, uuid)

    draw(provdoc,uuid+"send_request")

#def 


print("####################")
uuid = get_uuid()
print("ID: "+uuid)

send_request(uuid)
