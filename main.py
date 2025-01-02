from classes.provenance import Provenance

from modules.constants import Constants
from modules.utils import serialize, deserialize, draw, get_uuid, save, visualize_prov, create_prov_state_machine


def send_request(uuid):
    # Create Provenance Document
    provdoc = Provenance.init_document()

    # Create Namespace de Requester and Eletric Company
    nm_requester = Provenance.create_namespace(provdoc, Constants.NM_REQUESTER["prefix"], Constants.NM_REQUESTER["uri"])
    nm_ec = Provenance.create_namespace(provdoc, Constants.NM_EC["prefix"], Constants.NM_EC["uri"])
    
    # Create Agent Requester and Eletric Company
    requester = Provenance.create_agent(provdoc, nm_requester[Constants.AGENT_ID_Requester], Constants.AGENT_TYPE_PERSON, '11111111A')
    electric_company = Provenance.create_agent(provdoc, nm_ec[Constants.AGENT_ID_EC], Constants.AGENT_TYPE_ORGANIZATION, 'Power Supply Gmbh')

    # Create entity Initial Documentation
    documentation = Provenance.create_entity(provdoc, nm_requester['Documentation'], 'Initial Documentation')
    Provenance.wasAttributedTo(provdoc, documentation, requester)

    # Create Activity "Send Documentation to Electric Company"
    send_to_ec = Provenance.create_activity(provdoc, nm_requester['SendToEC'], "Send Documentation to Electric Company")
    Provenance.wasAssociatedWith(provdoc, send_to_ec, requester)
    Provenance.wasAssociatedWith(provdoc, send_to_ec, electric_company)
    Provenance.used(provdoc, send_to_ec, documentation)
    Provenance.wasGeneratedBy(provdoc, documentation, send_to_ec)

    save(provdoc, uuid,"1_send_request" )

def check_documentation(uuid):

    # Get ProvDoc
    provdoc = deserialize(uuid)

    # Get Namespace and agent Electric Company
    nm_ec = Provenance.get_namespace_by_id(provdoc, Constants.NM_EC["prefix"])
    electric_company = Provenance.get_agent_by_id(provdoc, nm_ec[Constants.AGENT_ID_EC])

    # Get Namespace and agent Requester
    nm_requester = Provenance.get_namespace_by_id(provdoc, Constants.NM_REQUESTER["prefix"])
    requester = Provenance.get_agent_by_id(provdoc, nm_requester[Constants.AGENT_ID_Requester])

    # Get Activity Send to EC
    send_to_ec = Provenance.get_activity_by_id(provdoc, nm_requester['SendToEC'])

    # Get Documentation entity
    documentation = Provenance.get_entity_by_id(provdoc, nm_requester['Documentation'])

    # Create entity documentation checked
    documentation_checked = Provenance.create_entity(provdoc, nm_ec['DocumentationChecked'], 'Documentation checked')
    Provenance.wasDerivedFrom(provdoc, documentation_checked, documentation)
    Provenance.wasAttributedTo(provdoc, documentation_checked, electric_company)

    # Create activity Check Documentation
    documentation_check = Provenance.create_activity(provdoc, nm_ec['CheckDocumentation'], "Check Documentation")
    Provenance.wasAssociatedWith(provdoc, documentation_check, electric_company)
    Provenance.wasInformedBy(provdoc, documentation_check, send_to_ec)
    Provenance.used(provdoc, documentation_check, documentation)
    Provenance.wasGeneratedBy(provdoc, documentation_checked, documentation_check)

    save(provdoc, uuid,"2_check_documentation" )

def send_documentation_checked_to_gov(uuid):

    # Get ProvDoc
    provdoc = deserialize(uuid)

    # Get Namespace and agent Electric Company
    nm_ec = Provenance.get_namespace_by_id(provdoc, Constants.NM_EC["prefix"])
    electric_company = Provenance.get_agent_by_id(provdoc, nm_ec[Constants.AGENT_ID_EC])

    # Get Namespace and agent Requester
    nm_requester = Provenance.get_namespace_by_id(provdoc, Constants.NM_REQUESTER["prefix"])
    requester = Provenance.get_agent_by_id(provdoc, nm_requester[Constants.AGENT_ID_Requester])

    # Get Activity Send to EC
    documentation_check = Provenance.get_activity_by_id(provdoc, nm_ec['CheckDocumentation'])

    # Get Documentation entity
    documentation_checked = Provenance.get_entity_by_id(provdoc, nm_ec['DocumentationChecked'])

    # Create Namespace de Gov
    nm_gov = Provenance.create_namespace(provdoc, Constants.NM_GOV["prefix"],Constants.NM_GOV["uri"])
    
    # Create Agent BOSCO
    bosco = Provenance.create_agent(provdoc, nm_gov[Constants.AGENT_ID_BOSCO], Constants.AGENT_TYPE_SOFTWARE, 'BOSCO')

    # Create activity Send to Gov
    send_to_gov = Provenance.create_activity(provdoc, nm_ec['SendToGov'],"Send Documentation to Government" )
    Provenance.wasInformedBy(provdoc, send_to_gov, documentation_check)
    Provenance.used(provdoc, send_to_gov, documentation_checked)
    Provenance.actedOnBehalfOf(provdoc, electric_company, requester, send_to_gov)
    Provenance.wasAssociatedWith(provdoc, send_to_gov, electric_company)
    Provenance.wasAssociatedWith(provdoc, send_to_gov, bosco)

    save(provdoc, uuid,"3_send_documentation_checked_to_gov" )


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

def send_decision_to_requester(uuid):
    # Get ProvDoc
    provdoc = deserialize(uuid)

    # Get Namespace Gov and agent BOSCO
    nm_gov = Provenance.get_namespace_by_id(provdoc, Constants.NM_GOV["prefix"])
    bosco = Provenance.get_agent_by_id(provdoc, nm_gov[Constants.AGENT_ID_BOSCO])

    # Get Namespace and agent Requester
    nm_requester = Provenance.get_namespace_by_id(provdoc, Constants.NM_REQUESTER["prefix"])
    requester = Provenance.get_agent_by_id(provdoc, nm_requester[Constants.AGENT_ID_Requester])

    # Get Namespace and agent Electric Company
    nm_ec = Provenance.get_namespace_by_id(provdoc, Constants.NM_EC["prefix"])
    electric_company = Provenance.get_agent_by_id(provdoc, nm_ec[Constants.AGENT_ID_EC])
    
    # Get Decision entity
    decision = Provenance.get_entity_by_id(provdoc, nm_gov['Decision'])

    # Get SendDecision
    send_decision_to_ec = Provenance.get_activity_by_id(provdoc, nm_gov['SendDecision'])

    # EC send decision to Requester
    send_decision_to_requester = Provenance.create_activity(provdoc, nm_ec['SendDecision'],"Send the Decision to Requester")   
    Provenance.wasAssociatedWith(provdoc, send_decision_to_requester, requester)
    Provenance.wasAssociatedWith(provdoc, send_decision_to_requester, electric_company)
    Provenance.used(provdoc, send_decision_to_requester, decision)
    Provenance.wasInformedBy(provdoc, send_decision_to_requester, send_decision_to_ec)
    Provenance.actedOnBehalfOf(provdoc, electric_company, bosco, send_decision_to_requester)

    save(provdoc, uuid,"9_send_decision_to_requester" )

    #visualize_prov(provdoc, output_path="outputs/"+uuid+"/prov_flow_networkx.png")
    create_prov_state_machine(provdoc, output_path="outputs/"+uuid+"/prov_flow_networkx.png")

print("####################")
uuid = get_uuid()
print("ID: "+uuid)

send_request(uuid)
check_documentation(uuid)
send_documentation_checked_to_gov(uuid)
bosco_preprocess_documentation(uuid)
bosco_ask_information_to_tax_office(uuid)
bosco_cross_data(uuid)
bosco_make_decision(uuid)
send_decision_to_ec(uuid)
send_decision_to_requester(uuid)

