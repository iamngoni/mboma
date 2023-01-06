class WhatsAppTextButton:
    def __init__(self, text, index, sub_type="quick_reply"):
        self.text = text
        self.index = index
        self.sub_type = sub_type

    def to_json(self):
        return {
            "type": "button",
            "sub_type": self.sub_type,
            "index": self.index,
            "parameters": [{"type": "text", "text": self.text}],
        }
