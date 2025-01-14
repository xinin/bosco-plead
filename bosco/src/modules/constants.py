class Constants:

    # NAMESPACES
    NM_REQUESTER = {
        "prefix": "requester",
        "uri": 'https://dictionary.cambridge.org/es/diccionario/ingles/requester'
    }
    NM_EC = {
        "prefix": "ec",
        "uri": 'https://example.org/electric_company'
    }
    NM_GOV = {
        "prefix": "gov",
        "uri": 'https://en.wikipedia.org/wiki/Government'
    }

    # AGENT TYPES
    AGENT_TYPE_PERSON = "Person"
    AGENT_TYPE_ORGANIZATION = "Organization"
    AGENT_TYPE_SOFTWARE = "SoftwareAgent"

    # AGENT IDS
    AGENT_ID_Requester = "Requester"
    AGENT_ID_EC = "EC"
    AGENT_ID_BOSCO = "BOSCO"
    AGENT_ID_TAX_OFFICE = "TAX"

    # REQUEST STATUS
    REQUEST_STATUS_OK = 1
    REQUEST_STATUS_KO = 2
    REQUEST_STATUS_PENDING = 3
