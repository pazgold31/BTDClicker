from collections import UserList

from common.monkey_knowledge.knowledge_crawler import get_monkey_knowledge_info, update_monkey_knowledge_info


class MonkeyKnowledge(UserList):

    def __init__(self):
        super(MonkeyKnowledge, self).__init__(get_monkey_knowledge_info())

    def update_info(self):
        update_monkey_knowledge_info()
        self.data = get_monkey_knowledge_info()


g_monkey_knowledge = MonkeyKnowledge()
