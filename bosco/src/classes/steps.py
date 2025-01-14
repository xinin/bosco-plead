from classes.provenance import Provenance
from classes.tax_office import TaxOffice
from modules.constants import Constants

from modules.constants import Constants
from modules.utils import deserialize, save, load_json, save_json, make_post_request


def bosco_preprocess_documentation(uuid):
    # Get ProvDoc
    provdoc = deserialize(uuid)

    # Get Namespace EC
    nm_ec = Provenance.get_namespace_by_id(provdoc, Constants.NM_EC["prefix"])

    # Get Namespace Gov and agent BOSCO
    nm_gov = Provenance.get_namespace_by_id(provdoc, Constants.NM_GOV["prefix"])
    bosco = Provenance.get_agent_by_id(provdoc, nm_gov[Constants.AGENT_ID_BOSCO])

    # Get Documentation entity
    documentation_checked = Provenance.get_entity_by_id(
        provdoc, nm_ec["DocumentationChecked"]
    )

    # Get Activity Send to EC
    send_to_gov = Provenance.get_activity_by_id(provdoc, nm_ec["SendToGov"])

    # BOSCO preprocess documentation
    preprocess_documentation = Provenance.create_activity(
        provdoc, nm_gov["PreprocessDocumentation"], "Preprocess Documentation by BOSCO"
    )
    Provenance.wasAssociatedWith(provdoc, preprocess_documentation, bosco)
    Provenance.wasInformedBy(provdoc, preprocess_documentation, send_to_gov)
    Provenance.used(provdoc, preprocess_documentation, documentation_checked)
    Provenance.wasAssociatedWith(provdoc, preprocess_documentation, bosco)

    save(provdoc, uuid, "4_bosco_preprocess_documentation")


def bosco_ask_information_to_tax_office(uuid):
    # Get ProvDoc
    provdoc = deserialize(uuid)

    # Get Namespace Gov and agent BOSCO
    nm_gov = Provenance.get_namespace_by_id(provdoc, Constants.NM_GOV["prefix"])
    bosco = Provenance.get_agent_by_id(provdoc, nm_gov[Constants.AGENT_ID_BOSCO])

    # Get Activity Send to EC
    preprocess_documentation = Provenance.get_activity_by_id(
        provdoc, nm_gov["PreprocessDocumentation"]
    )

    # Create Agent Tax Office
    tax_office = Provenance.create_agent(
        provdoc,
        nm_gov[Constants.AGENT_ID_TAX_OFFICE],
        Constants.AGENT_TYPE_ORGANIZATION,
        "TAX OFFICE",
    )

    # BOSCO ask information from the Tax Office
    retrieve_tax_info = Provenance.create_activity(
        provdoc, nm_gov["RetrieveTaxInfo"], "Retrieves Tax Info"
    )
    Provenance.wasAssociatedWith(provdoc, retrieve_tax_info, tax_office)
    Provenance.wasAssociatedWith(provdoc, retrieve_tax_info, bosco)
    Provenance.wasInformedBy(provdoc, retrieve_tax_info, preprocess_documentation)
    Provenance.wasAssociatedWith(provdoc, retrieve_tax_info, tax_office)

    # Get request data
    data = load_json(uuid)
    tax_office_data = TaxOffice.get_data(data.get("dni"))

    if not tax_office_data:
        data["status"] = Constants.REQUEST_STATUS_KO
        data["msg"] = "There are not tax data available."

        # Create entity Decision
        decision = Provenance.create_entity(provdoc, nm_gov["Decision"], "Decision")
        Provenance.wasAttributedTo(provdoc, decision, bosco)
        Provenance.wasGeneratedBy(provdoc, decision, retrieve_tax_info)
        Provenance.wasDerivedFrom(provdoc, decision, retrieve_tax_info)

        save(provdoc, uuid, "5_bosco_ask_tax_info")
        save_json(uuid, data)

        return False

    # Create entity TAX INFO
    tax_info = Provenance.create_entity(provdoc, nm_gov["TaxInfo"], "Tax Information")
    Provenance.wasAttributedTo(provdoc, tax_info, tax_office)
    Provenance.wasGeneratedBy(provdoc, tax_info, retrieve_tax_info)

    save(provdoc, uuid, "5_bosco_ask_tax_info")

    return tax_office_data


def bosco_cross_data(uuid, tax_office_data):
    # Get ProvDoc
    provdoc = deserialize(uuid)

    # Get Namespace EC
    nm_ec = Provenance.get_namespace_by_id(provdoc, Constants.NM_EC["prefix"])

    # Get Namespace Gov and agent BOSCO
    nm_gov = Provenance.get_namespace_by_id(provdoc, Constants.NM_GOV["prefix"])
    bosco = Provenance.get_agent_by_id(provdoc, nm_gov[Constants.AGENT_ID_BOSCO])

    # Get Documentation entity
    documentation_checked = Provenance.get_entity_by_id(
        provdoc, nm_ec["DocumentationChecked"]
    )

    # Get Tax Info
    tax_info = Provenance.get_entity_by_id(provdoc, nm_gov["TaxInfo"])

    # Get Activity RetrieveTaxInfo
    retrieve_tax_info = Provenance.get_activity_by_id(
        provdoc, nm_gov["RetrieveTaxInfo"]
    )

    # Create Activity Cross Data
    cross_data = Provenance.create_activity(
        provdoc, nm_gov["CrossData"], "Cross Data Info"
    )
    Provenance.wasAssociatedWith(provdoc, cross_data, bosco)
    Provenance.wasInformedBy(provdoc, cross_data, retrieve_tax_info)

    data = load_json(uuid)
    merged_data = {**tax_office_data, **data}
    save_json(uuid, merged_data)

    # create entity Data Crossed
    data_crossed = Provenance.create_entity(
        provdoc, nm_gov["DataCrossed"], "Data Crossed"
    )
    Provenance.wasAttributedTo(provdoc, data_crossed, bosco)
    Provenance.wasGeneratedBy(provdoc, data_crossed, cross_data)
    Provenance.used(provdoc, data_crossed, tax_info)
    Provenance.used(provdoc, data_crossed, documentation_checked)
    Provenance.wasDerivedFrom(provdoc, data_crossed, tax_info)
    Provenance.wasDerivedFrom(provdoc, data_crossed, documentation_checked)

    save(provdoc, uuid, "6_data_crossed")
    return merged_data


def bosco_make_decision(uuid):

    def decide(civil_status, genre, incomes, dependent_children):
        # Caso 1: Viuda, sin importar el número de hijos, si tiene ingresos bajos
        if civil_status == "widow":
            if incomes < 10000:
                return {
                    "status": Constants.REQUEST_STATUS_OK,
                    "msg": "Eligible: widow with low income",
                }
            elif dependent_children > 0:
                return {
                    "status": Constants.REQUEST_STATUS_OK,
                    "msg": "Eligible: Widow with dependent children.",
                }
            else:
                return {
                    "status": Constants.REQUEST_STATUS_KO,
                    "msg": "Not eligible: Widowed, but income over €10,000.",
                }

        # Caso 2: Ingresos bajos (< 10,000€) y tiene hijos dependientes
        if incomes < 10000 and dependent_children > 0:
            return {
                "status": Constants.REQUEST_STATUS_OK,
                "msg": "Eligible: Low income and has dependent children.",
            }

        # Caso 3: Soltera, con ingresos bajos o con hijos dependientes
        if civil_status == "single":
            if incomes < 10000:
                return {
                    "status": Constants.REQUEST_STATUS_OK,
                    "msg": "Eligible: Single with low income.",
                }
            elif dependent_children > 0 and incomes < 20000:
                return {
                    "status": Constants.REQUEST_STATUS_OK,
                    "msg": "Eligible: Single with dependent children and low incomes.",
                }
            else:
                return {
                    "status": Constants.REQUEST_STATUS_KO,
                    "msg": "Not eligible: Single with income over €10,000 and no dependent children.",
                }

        # Caso 4: Casada, no se le concede ayuda si tiene ingresos superiores a 10,000€ sin hijos
        if civil_status == "married":
            if incomes < 10000:
                if dependent_children > 0:
                    return {
                        "status": Constants.REQUEST_STATUS_OK,
                        "msg": "Eligible: Married, but with dependent children.",
                    }
                else:
                    return {
                        "status": Constants.REQUEST_STATUS_KO,
                        "msg": "Not eligible: Married with low income, but no dependent children.",
                    }
            else:
                return {
                    "status": Constants.REQUEST_STATUS_KO,
                    "msg": "Eligible: Married with income over €10,000.",
                }

        # Si no cumple con ninguno de los casos, no merece la ayuda
        return {
            "status": Constants.REQUEST_STATUS_KO,
            "msg": "Not eligible: Does not meet clear eligibility requirements.",
        }

    # Get ProvDoc
    provdoc = deserialize(uuid)

    # Get Namespace Gov and agent BOSCO
    nm_gov = Provenance.get_namespace_by_id(provdoc, Constants.NM_GOV["prefix"])
    bosco = Provenance.get_agent_by_id(provdoc, nm_gov[Constants.AGENT_ID_BOSCO])

    # Get Activity CrossData
    cross_data = Provenance.get_activity_by_id(provdoc, nm_gov["CrossData"])

    # Get Data Crossed entity
    data_crossed = Provenance.get_entity_by_id(provdoc, nm_gov["DataCrossed"])

    # Create Activity Make a Decision
    make_decision = Provenance.create_activity(
        provdoc, nm_gov["MakeDecision"], "Make a Decision"
    )
    Provenance.wasAssociatedWith(provdoc, make_decision, bosco)
    Provenance.wasInformedBy(provdoc, make_decision, cross_data)

    # Get Crossed Data
    data = load_json(uuid)
    bosco_decision = decide(
        data.get("civil_status"),
        data.get("genre"),
        data.get("incomes"),
        data.get("dependent_children"),
    )

    # Create entity Decision
    decision = Provenance.create_entity(provdoc, nm_gov["Decision"], "Decision")
    Provenance.wasAttributedTo(provdoc, decision, bosco)
    Provenance.wasGeneratedBy(provdoc, decision, make_decision)
    Provenance.used(provdoc, make_decision, data_crossed)
    Provenance.wasDerivedFrom(provdoc, decision, data_crossed)

    save(provdoc, uuid, "7_make_decision")

    data["status"] = bosco_decision["status"]
    data["msg"] = bosco_decision["msg"]
    save_json(uuid, data)


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
    decision = Provenance.get_entity_by_id(provdoc, nm_gov["Decision"])

    # Get MakeDecision
    try:
        make_decision = Provenance.get_activity_by_id(provdoc, nm_gov["MakeDecision"])
    except ValueError:
        make_decision = None

    # BOSCO send decision to EC
    send_decision_to_ec = Provenance.create_activity(
        provdoc, nm_gov["SendDecision"], "Send the Decision to EC"
    )
    Provenance.wasAssociatedWith(provdoc, send_decision_to_ec, bosco)
    Provenance.wasAssociatedWith(provdoc, send_decision_to_ec, electric_company)
    Provenance.used(provdoc, send_decision_to_ec, decision)
    if make_decision:
        Provenance.wasInformedBy(provdoc, send_decision_to_ec, make_decision)

    save(provdoc, uuid, "8_send_decision_to_ec")

    make_post_request("http://electric_company_back:8080/api/decision", {"uuid": uuid})
