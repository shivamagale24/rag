class ConversationMemory:

    def __init__(self, max_messages=6):
        self.max_messages = max_messages
        self.messages = []

    def add_message(
        self,
        question,
        answer
    ):
        self.messages.append(
            {
                "question": question,
                "answer": answer
            }
        )

        self.messages = self.messages[
            -self.max_messages:
        ]

    def get_history(self):
        return self.messages

    def clear(self):
        self.messages = []

    def is_empty(self):
        return len(self.messages) == 0