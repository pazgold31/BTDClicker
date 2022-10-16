from common.monkey_knowledge.knowledge_crawler import get_monkey_knowledge_info, update_monkey_knowledge_info
from common.singleton import Singleton


class MonkeyKnowledge(metaclass=Singleton):
    def __init__(self):
        self._knowledge = get_monkey_knowledge_info()

    def get_knowledge(self):
        return self._knowledge

    def update_knowledge(self):
        update_monkey_knowledge_info()
        self._knowledge = get_monkey_knowledge_info()
