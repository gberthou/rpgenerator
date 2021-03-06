import random
import quest

def generate_syllable():
    vowels     = list("aeiouy")
    consonants = list("bcdfghjklmnpqrstvwxz")

    random.shuffle(vowels)
    random.shuffle(consonants)

    return vowels[0] + consonants[0]

class Lore:
    def __init__(self):
        self.villages = set()
        self.npcs     = set()
        self.items    = set()

    def create_quest(self, is_unmissable, distinct_from, compatible_with):
        # Simple algorithm:
        # unmissable => Go to new village
        # missable   => Fight NPC

        if is_unmissable:
            # Create a new village and create a new quest that consists in going to this village
            return quest.QuestGoTo(self.create_village())

        # Otherwise, create a "fight" quest 

        # Take into account "compatible_with" constraints, i.e., don't use entities that were disabled by preceding edges
        disabled_entities  = set(npc for edge in compatible_with for npc in edge.quest.disables_entities)

        # Take into account "distinct_from" constraints, i.e., don't target the same npc as other egdes coming from the same node
        disabled_entities |= set(edge.quest.npc for edge in distinct_from if edge.quest.quest_type == quest.QuestType.FIGHT_NPC)

        # Remove the disabled entities from the set of available npcs
        available_npcs_to_fight = self.npcs - disabled_entities

        # If at least one NPC is available, do not create a new one
        if len(available_npcs_to_fight) > 0:
            npc = random.choice(tuple(available_npcs_to_fight))
            return quest.QuestFight(npc)

        # Otherwise, create a new npc
        npc = self.create_npc()
        return quest.QuestFight(npc)
    
    def create_village(self):
        count = random.randint(1, 4)
        
        # TODO: Remove possible infinite loop
        name = "".join(generate_syllable() for i in range(count)).title()
        while name in self.villages:
            name = "".join(generate_syllable() for i in range(count)).title()
        self.villages |= {name}
        return name

    def create_npc(self):
        first_name = "".join(generate_syllable() for i in range(random.randint(1, 4)))
        last_name = "".join(generate_syllable() for i in range(random.randint(1, 4)))
        name = (first_name + " " + last_name).title()
        self.npcs |= {name}
        return name

    def create_item(self):
        return None
            
