from classes.provenance import Provenance
from modules.constants import Constants

from modules.utils import deserialize, save, save_json, make_post_request, load_json
from modules.constants import Constants


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
        requester_data.get("dni"),
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

    return True


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

    # Get Activity Send to EC
    send_to_ec = Provenance.get_activity_by_id(provdoc, nm_requester["SendToEC"])

    # Get Documentation entity
    documentation = Provenance.get_entity_by_id(provdoc, nm_requester["Documentation"])

    # Get request information
    data = load_json(uuid)

    # Create activity Check Documentation
    documentation_check = Provenance.create_activity(
        provdoc, nm_ec["CheckDocumentation"], "Check Documentation"
    )
    Provenance.wasAssociatedWith(provdoc, documentation_check, electric_company)
    Provenance.wasInformedBy(provdoc, documentation_check, send_to_ec)
    Provenance.used(provdoc, documentation_check, documentation)

    # Check Documentation
    print("VERIFICANDO DATOS")
    required_fields = ["name", "surname", "dni", "email"]
    for field in required_fields:
        print("FIELD", field, data[field])
        if not data.get(field):
            msg = f"Check documentation failed. Field '{field}' is mandatory and it can not be None."
            data["status"] = Constants.REQUEST_STATUS_KO
            data["msg"] = msg
            save_json(uuid, data)

            # Create entity documentation invalid
            documentation_invalid = Provenance.create_entity(
                provdoc, nm_ec["DocumentationInvalid"], "Documentation invalid"
            )
            Provenance.wasDerivedFrom(provdoc, documentation_invalid, documentation)
            Provenance.wasAttributedTo(provdoc, documentation_invalid, electric_company)
            Provenance.wasGeneratedBy(
                provdoc, documentation_invalid, documentation_check
            )

            save(provdoc, uuid, "2_check_documentation")

            return False

    # Create entity documentation checked
    documentation_checked = Provenance.create_entity(
        provdoc, nm_ec["DocumentationChecked"], "Documentation checked"
    )
    Provenance.wasDerivedFrom(provdoc, documentation_checked, documentation)
    Provenance.wasAttributedTo(provdoc, documentation_checked, electric_company)
    Provenance.wasGeneratedBy(provdoc, documentation_checked, documentation_check)

    save(provdoc, uuid, "2_check_documentation")

    return True


def send_documentation_checked_to_gov(uuid):

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

    # Send request to BOSCO
    make_post_request("http://bosco:8081/api/data", {"uuid": uuid})

    save(provdoc, uuid, "3_send_documentation_checked_to_gov")

    return True


def send_decision_to_requester(uuid):
    
    # Get ProvDoc
    provdoc = deserialize(uuid)

    # Get Namespace Gov and agent BOSCO
    nm_gov = Provenance.get_namespace_by_id(provdoc, Constants.NM_GOV["prefix"])
    bosco = Provenance.get_agent_by_id(provdoc, nm_gov[Constants.AGENT_ID_BOSCO])

    # Get Namespace and agent Requester
    nm_requester = Provenance.get_namespace_by_id(
        provdoc, Constants.NM_REQUESTER["prefix"]
    )
    requester = Provenance.get_agent_by_id(
        provdoc, nm_requester[Constants.AGENT_ID_Requester]
    )

    # Get Namespace and agent Electric Company
    nm_ec = Provenance.get_namespace_by_id(provdoc, Constants.NM_EC["prefix"])
    electric_company = Provenance.get_agent_by_id(provdoc, nm_ec[Constants.AGENT_ID_EC])

    # Get Decision entity
    decision = Provenance.get_entity_by_id(provdoc, nm_gov["Decision"])

    # Get SendDecision
    send_decision_to_ec = Provenance.get_activity_by_id(provdoc, nm_gov["SendDecision"])

    # EC send decision to Requester
    ac_send_decision_to_requester = Provenance.create_activity(
        provdoc, nm_ec["SendDecision"], "Send the Decision to Requester"
    )
    Provenance.wasAssociatedWith(provdoc, ac_send_decision_to_requester, requester)
    Provenance.wasAssociatedWith(provdoc, ac_send_decision_to_requester, electric_company)
    Provenance.used(provdoc, ac_send_decision_to_requester, decision)
    Provenance.wasInformedBy(provdoc, ac_send_decision_to_requester, send_decision_to_ec)
    Provenance.actedOnBehalfOf(
        provdoc, electric_company, bosco, ac_send_decision_to_requester
    )

    save(provdoc, uuid, "9_send_decision_to_requester")
