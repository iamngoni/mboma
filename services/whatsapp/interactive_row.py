class InteractiveRow:
    def __init__(self, id: str, title: str, description: str):
        self.id = id
        self.title = title
        self.description = description

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
        }
