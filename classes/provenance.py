from prov.model import ProvDocument, PROV

class Provenance:

    @staticmethod
    def init_document():
        return ProvDocument()

    @staticmethod
    def create_namespace(provdoc, name, uri):
        return provdoc.add_namespace(name, uri)

    @staticmethod
    def get_namespace_by_id(provdoc: ProvDocument, prefix: str):
        """
        Busca un namespace en el ProvDocument por su prefijo.
        
        Args:
            document (ProvDocument): El documento PROV donde buscar el namespace.
            prefix (str): El prefijo del namespace que deseas encontrar.
        
        Returns:
            ProvNamespace: El namespace correspondiente al prefijo.
        
        Raises:
            ValueError: Si el namespace con el prefijo dado no existe.
        """
        for namespace in provdoc.namespaces:
            if namespace.prefix == prefix:
                return namespace
        raise ValueError(f"Namespace with prefix '{prefix}' not found.")

    @staticmethod
    def create_agent(provdoc, id, agent_type, label):
        return provdoc.agent(id, {"prov:type": PROV[agent_type], "prov:label": label})

    @staticmethod
    def create_entity(provdoc, id, label):
        return provdoc.entity(id, {"prov:label": label})

    @staticmethod
    def wasAttributedTo(provdoc, entity, agent):
        provdoc.wasAttributedTo(entity, agent)

    @staticmethod
    def create_activity(provdoc, id, label):
        activity = provdoc.activity(id)
        activity.add_attributes({"prov:label": label})
        return activity
    
    @staticmethod
    def wasAssociatedWith(provdoc, activity, agent):
        provdoc.wasAssociatedWith(activity, agent)

    @staticmethod
    def used(provdoc, activity, entity):
        provdoc.used(activity, entity)

    @staticmethod
    def wasGeneratedBy(provdoc, entity, activity):
        provdoc.wasGeneratedBy(entity, activity)

  