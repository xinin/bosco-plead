from prov.model import ProvDocument
from prov.dot import prov_to_dot

import datetime

# Definición de las clases principales para cada tipo de elemento PROV-N
class Entity:
    def __init__(self, entity_id, description=None):
        self.entity_id = entity_id
        self.description = description
        self.generated_by = None
        self.was_used_by = []
    
    def __str__(self):
        return f"Entity({self.entity_id}, {self.description})"
    
class Activity:
    def __init__(self, activity_id, start_time=None, end_time=None, description=None):
        self.activity_id = activity_id
        self.start_time = start_time if start_time else datetime.datetime.now()
        self.end_time = end_time
        self.description = description
        self.used_entities = []
        self.generated_entities = []
        self.associated_agents = []
    
    def __str__(self):
        return f"Activity({self.activity_id}, {self.start_time}, {self.end_time}, {self.description})"

    def add_used_entity(self, entity):
        self.used_entities.append(entity)
        entity.was_used_by.append(self)
    
    def add_generated_entity(self, entity):
        self.generated_entities.append(entity)
        entity.generated_by = self

    def add_agent(self, agent):
        self.associated_agents.append(agent)
        
class Agent:
    def __init__(self, agent_id, name):
        self.agent_id = agent_id
        self.name = name
        self.was_associated_with_activities = []
    
    def __str__(self):
        return f"Agent({self.agent_id}, {self.name})"

    def associate_with_activity(self, activity):
        self.was_associated_with_activities.append(activity)
        activity.add_agent(self)

# Funciones para generar y representar relaciones PROV-N
def generate_provn_notation(entities, activities, agents):
    provn = []
    
    for entity in entities:
        provn.append(f"Entity({entity.entity_id})")
        if entity.description:
            provn.append(f"    {entity.description}")
        if entity.generated_by:
            provn.append(f"    wasGeneratedBy({entity.entity_id}, {entity.generated_by.activity_id})")
        for activity in entity.was_used_by:
            provn.append(f"    wasUsedBy({entity.entity_id}, {activity.activity_id})")
    
    for activity in activities:
        provn.append(f"Activity({activity.activity_id})")
        if activity.description:
            provn.append(f"    {activity.description}")
        if activity.start_time:
            provn.append(f"    startedAt({activity.activity_id}, {activity.start_time})")
        if activity.end_time:
            provn.append(f"    endedAt({activity.activity_id}, {activity.end_time})")
        for entity in activity.used_entities:
            provn.append(f"    used({activity.activity_id}, {entity.entity_id})")
        for entity in activity.generated_entities:
            provn.append(f"    generated({activity.activity_id}, {entity.entity_id})")
        for agent in activity.associated_agents:
            provn.append(f"    wasAssociatedWith({activity.activity_id}, {agent.agent_id})")
    
    for agent in agents:
        provn.append(f"Agent({agent.agent_id})")
        provn.append(f"    {agent.name}")
    
    return "\n".join(provn)

# Ejemplo de uso
entity1 = Entity("e1", "Data file")
entity2 = Entity("e2", "Processed data")
activity1 = Activity("a1", description="Data processing")
activity2 = Activity("a2", description="Data validation")
agent1 = Agent("ag1", "Researcher")

# Estableciendo relaciones
activity1.add_used_entity(entity1)
activity1.add_generated_entity(entity2)
activity1.add_agent(agent1)

activity2.add_used_entity(entity2)
activity2.add_agent(agent1)

# Generar notación PROV-N
entities = [entity1, entity2]
activities = [activity1, activity2]
agents = [agent1]

provn_notation = generate_provn_notation(entities, activities, agents)
print(provn_notation)

dot = prov_to_dot(provn_notation)
dot.write_png('article-prov.png')