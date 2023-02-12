#
#  reply_button.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 12/2/2023.


class ReplyButton:
    def __init__(self, button_id: str, title: str):
        self.id = button_id
        self.title = title

    def to_json(self) -> dict:
        return {
            "type": "reply",
            "reply": {
                "id": self.id,
                "title": self.title,
            },
        }
