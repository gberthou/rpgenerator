import enum

class QuestType(enum.IntEnum):
    GO_TO    = 0
    FIGHT_NPC = 1

class Quest:
    def __init__(self, quest_type, involved_entities, disables_entities):
        self.quest_type = quest_type
        self.involved_entities = involved_entities
        self.disables_entities = disables_entities

class QuestGoTo(Quest):
    def __init__(self, village):
        Quest.__init__(self, QuestType.GO_TO, {village}, set())
        self.village = village

    def __str__(self):
        return "Go to %s" % self.village

class QuestFight(Quest):
    def __init__(self, npc):
        Quest.__init__(self, QuestType.FIGHT_NPC, {npc}, {npc})
        self.npc = npc

    def __str__(self):
        return "Fight %s" % self.npc
