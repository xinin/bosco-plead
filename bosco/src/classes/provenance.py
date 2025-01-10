from prov.model import ProvDocument, ProvAgent, ProvActivity, ProvEntity, PROV

class Provenance:
    # ---- Operaciones básicas del documento ----
    @staticmethod
    def init_document() -> ProvDocument:
        """
        Inicializa un nuevo documento PROV.

        Returns:
            ProvDocument: Un documento PROV vacío.
        """
        return ProvDocument()

    # ---- Gestión de namespaces ----
    @staticmethod
    def create_namespace(provdoc: ProvDocument, name: str, uri: str):
        """
        Crea un nuevo namespace en el documento PROV.

        Args:
            provdoc (ProvDocument): El documento PROV donde agregar el namespace.
            name (str): El prefijo del namespace.
            uri (str): La URI asociada al namespace.

        Returns:
            ProvNamespace: El namespace creado.
        """
        return provdoc.add_namespace(name, uri)

    @staticmethod
    def get_namespace_by_id(provdoc: ProvDocument, prefix: str):
        """
        Busca un namespace en el documento PROV por su prefijo.

        Args:
            provdoc (ProvDocument): El documento PROV donde buscar el namespace.
            prefix (str): El prefijo del namespace.

        Returns:
            ProvNamespace: El namespace correspondiente.

        Raises:
            ValueError: Si el namespace no existe.
        """
        for namespace in provdoc.namespaces:
            if namespace.prefix == prefix:
                return namespace
        raise ValueError(f"Namespace with prefix '{prefix}' not found.")

    # ---- Gestión de agentes ----
    @staticmethod
    def create_agent(provdoc: ProvDocument, id: str, agent_type: str, label: str) -> ProvAgent:
        """
        Crea un nuevo agente en el documento PROV.

        Args:
            provdoc (ProvDocument): El documento PROV donde agregar el agente.
            id (str): El ID único del agente.
            agent_type (str): El tipo del agente (e.g., "Person", "Organization").
            label (str): La etiqueta descriptiva del agente.

        Returns:
            ProvAgent: El agente creado.
        """
        return provdoc.agent(id, {"prov:type": PROV[agent_type], "prov:label": label})

    @staticmethod
    def get_agent_by_id(provdoc: ProvDocument, agent_id: str) -> ProvAgent:
        """
        Busca un agente en el documento PROV por su ID.

        Args:
            provdoc (ProvDocument): El documento PROV donde buscar el agente.
            agent_id (str): El ID del agente.

        Returns:
            ProvAgent: El agente correspondiente.

        Raises:
            ValueError: Si el agente no existe.
        """
        for agent in provdoc.get_records(ProvAgent):
            if agent.identifier == agent_id:
                return agent
        raise ValueError(f"Agent with ID '{agent_id}' not found.")

    # ---- Gestión de actividades ----
    @staticmethod
    def create_activity(provdoc: ProvDocument, id: str, label: str) -> ProvActivity:
        """
        Crea una nueva actividad en el documento PROV.

        Args:
            provdoc (ProvDocument): El documento PROV donde agregar la actividad.
            id (str): El ID único de la actividad.
            label (str): La etiqueta descriptiva de la actividad.

        Returns:
            ProvActivity: La actividad creada.
        """
        activity = provdoc.activity(id)
        activity.add_attributes({"prov:label": label})
        return activity

    @staticmethod
    def get_activity_by_id(provdoc: ProvDocument, activity_id: str) -> ProvActivity:
        """
        Busca una actividad en el documento PROV por su ID.

        Args:
            provdoc (ProvDocument): El documento PROV donde buscar la actividad.
            activity_id (str): El ID de la actividad.

        Returns:
            ProvActivity: La actividad correspondiente.

        Raises:
            ValueError: Si la actividad no existe.
        """
        for activity in provdoc.get_records(ProvActivity):
            if str(activity.identifier) == str(activity_id):
                return activity
        raise ValueError(f"Activity with ID '{activity_id}' not found.")

    # ---- Gestión de entidades ----
    @staticmethod
    def create_entity(provdoc: ProvDocument, id: str, label: str) -> ProvEntity:
        """
        Crea una nueva entidad en el documento PROV.

        Args:
            provdoc (ProvDocument): El documento PROV donde agregar la entidad.
            id (str): El ID único de la entidad.
            label (str): La etiqueta descriptiva de la entidad.

        Returns:
            ProvEntity: La entidad creada.
        """
        return provdoc.entity(id, {"prov:label": label})

    @staticmethod
    def get_entity_by_id(provdoc: ProvDocument, entity_id: str) -> ProvEntity:
        """
        Busca una entidad en el documento PROV por su ID.

        Args:
            provdoc (ProvDocument): El documento PROV donde buscar la entidad.
            entity_id (str): El ID de la entidad.

        Returns:
            ProvEntity: La entidad correspondiente.

        Raises:
            ValueError: Si la entidad no existe.
        """
        for entity in provdoc.get_records(ProvEntity):
            if str(entity.identifier) == str(entity_id):
                return entity
        raise ValueError(f"Entity with ID '{entity_id}' not found.")

    # ---- Relaciones entre nodos ----
    @staticmethod
    def wasAttributedTo(provdoc: ProvDocument, entity: ProvEntity, agent: ProvAgent):
        """
        Relaciona una entidad con un agente, indicando que la entidad fue atribuida al agente.
        """
        provdoc.wasAttributedTo(entity, agent)

    @staticmethod
    def wasAssociatedWith(provdoc: ProvDocument, activity: ProvActivity, agent: ProvAgent):
        """
        Relaciona una actividad con un agente, indicando que el agente estuvo asociado a la actividad.
        """
        provdoc.wasAssociatedWith(activity, agent)

    @staticmethod
    def used(provdoc: ProvDocument, activity: ProvActivity, entity: ProvEntity):
        """
        Indica que una actividad utilizó una entidad.
        """
        provdoc.used(activity, entity)

    @staticmethod
    def wasGeneratedBy(provdoc: ProvDocument, entity: ProvEntity, activity: ProvActivity):
        """
        Indica que una entidad fue generada por una actividad.
        """
        provdoc.wasGeneratedBy(entity, activity)

    @staticmethod
    def wasInformedBy(provdoc: ProvDocument, activity1: ProvActivity, activity2: ProvActivity):
        """
        Indica que una actividad fue informada por otra.
        """
        provdoc.wasInformedBy(activity1, activity2)

    @staticmethod
    def wasDerivedFrom(provdoc: ProvDocument, entity2: ProvEntity, entity1: ProvEntity):
        """
        Indica que una entidad deriva de otra.
        """
        provdoc.wasDerivedFrom(entity2, entity1)

    @staticmethod
    def actedOnBehalfOf(provdoc: ProvDocument, agent2: ProvAgent, agent1: ProvAgent, activity: ProvActivity):
        """
        Indica que un agente actuó en nombre de otro en el contexto de una actividad.
        """
        provdoc.actedOnBehalfOf(agent2, agent1, activity)
