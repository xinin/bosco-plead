from classes.provenance import Provenance
from modules.constants import Constants

from modules.utils import deserialize, save, save_json, make_post_request

def create_request(uuid, requester_data):

    # Save Requester data
    save_json(uuid, requester_data)

    # Create Provenance Document
    provdoc = Provenance.init_document()

    # Create Namespace de Requester and Eletric Company
    nm_requester = Provenance.create_namespace(
        provdoc, Constants.NM_REQUESTER["prefix"], Constants.NM_REQUESTER["uri"]
    )
    nm_ec = Provenance.create_namespace(
        provdoc, Constants.NM_EC["prefix"], Constants.NM_EC["uri"]
    )

    # Create Agent Requester and Eletric Company
    requester = Provenance.create_agent(
        provdoc,
        nm_requester[Constants.AGENT_ID_Requester],
        Constants.AGENT_TYPE_PERSON,
        requester_data.get('dni'),
    )
    electric_company = Provenance.create_agent(
        provdoc,
        nm_ec[Constants.AGENT_ID_EC],
        Constants.AGENT_TYPE_ORGANIZATION,
        "Power Supply Gmbh",
    )

    # Create entity Initial Documentation
    documentation = Provenance.create_entity(
        provdoc, nm_requester["Documentation"], "Initial Documentation"
    )
    Provenance.wasAttributedTo(provdoc, documentation, requester)

    # Create Activity "Send Documentation to Electric Company"
    send_to_ec = Provenance.create_activity(
        provdoc, nm_requester["SendToEC"], "Send Documentation to Electric Company"
    )
    Provenance.wasAssociatedWith(provdoc, send_to_ec, requester)
    Provenance.wasAssociatedWith(provdoc, send_to_ec, electric_company)
    Provenance.used(provdoc, send_to_ec, documentation)
    Provenance.wasGeneratedBy(provdoc, documentation, send_to_ec)

    save(provdoc, uuid, "1_send_request")


def check_documentation(uuid):

    # Get ProvDoc
    provdoc = deserialize(uuid)

    # Get Namespace and agent Electric Company
    nm_ec = Provenance.get_namespace_by_id(provdoc, Constants.NM_EC["prefix"])
    electric_company = Provenance.get_agent_by_id(provdoc, nm_ec[Constants.AGENT_ID_EC])

    # Get Namespace and agent Requester
    nm_requester = Provenance.get_namespace_by_id(
        provdoc, Constants.NM_REQUESTER["prefix"]
    )
    requester = Provenance.get_agent_by_id(
        provdoc, nm_requester[Constants.AGENT_ID_Requester]
    )

    # Get Activity Send to EC
    send_to_ec = Provenance.get_activity_by_id(provdoc, nm_requester["SendToEC"])

    # Get Documentation entity
    documentation = Provenance.get_entity_by_id(provdoc, nm_requester["Documentation"])

    # Create entity documentation checked
    documentation_checked = Provenance.create_entity(
        provdoc, nm_ec["DocumentationChecked"], "Documentation checked"
    )
    Provenance.wasDerivedFrom(provdoc, documentation_checked, documentation)
    Provenance.wasAttributedTo(provdoc, documentation_checked, electric_company)

    # Create activity Check Documentation
    documentation_check = Provenance.create_activity(
        provdoc, nm_ec["CheckDocumentation"], "Check Documentation"
    )
    Provenance.wasAssociatedWith(provdoc, documentation_check, electric_company)
    Provenance.wasInformedBy(provdoc, documentation_check, send_to_ec)
    Provenance.used(provdoc, documentation_check, documentation)
    Provenance.wasGeneratedBy(provdoc, documentation_checked, documentation_check)

    save(provdoc, uuid, "2_check_documentation")


def send_documentation_checked_to_gov(uuid):

    make_post_request("http://bosco:8081/api/data", {"uuid": uuid})

    # Get ProvDoc
    provdoc = deserialize(uuid)

    # Get Namespace and agent Electric Company
    nm_ec = Provenance.get_namespace_by_id(provdoc, Constants.NM_EC["prefix"])
    electric_company = Provenance.get_agent_by_id(provdoc, nm_ec[Constants.AGENT_ID_EC])

    # Get Namespace and agent Requester
    nm_requester = Provenance.get_namespace_by_id(
        provdoc, Constants.NM_REQUESTER["prefix"]
    )
    requester = Provenance.get_agent_by_id(
        provdoc, nm_requester[Constants.AGENT_ID_Requester]
    )

    # Get Activity Send to EC
    documentation_check = Provenance.get_activity_by_id(
        provdoc, nm_ec["CheckDocumentation"]
    )

    # Get Documentation entity
    documentation_checked = Provenance.get_entity_by_id(
        provdoc, nm_ec["DocumentationChecked"]
    )

    # Create Namespace de Gov
    nm_gov = Provenance.create_namespace(
        provdoc, Constants.NM_GOV["prefix"], Constants.NM_GOV["uri"]
    )

    # Create Agent BOSCO
    bosco = Provenance.create_agent(
        provdoc,
        nm_gov[Constants.AGENT_ID_BOSCO],
        Constants.AGENT_TYPE_SOFTWARE,
        "BOSCO",
    )

    # Create activity Send to Gov
    send_to_gov = Provenance.create_activity(
        provdoc, nm_ec["SendToGov"], "Send Documentation to Government"
    )
    Provenance.wasInformedBy(provdoc, send_to_gov, documentation_check)
    Provenance.used(provdoc, send_to_gov, documentation_checked)
    Provenance.actedOnBehalfOf(provdoc, electric_company, requester, send_to_gov)
    Provenance.wasAssociatedWith(provdoc, send_to_gov, electric_company)
    Provenance.wasAssociatedWith(provdoc, send_to_gov, bosco)

    save(provdoc, uuid, "3_send_documentation_checked_to_gov")
