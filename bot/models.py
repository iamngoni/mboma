from django.db import models

from mboma.model import SoftDeleteModel
from loguru import logger


class WhatsappSession(SoftDeleteModel):
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    stage = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    payload = models.JSONField(blank=True, null=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone_number} | {self.stage} | {self.position} | {self.payload}"

    class Meta:
        db_table = "whatsapp_sessions"
        verbose_name = "Whatsapp Session"
        verbose_name_plural = "Whatsapp Sessions"
        table_prefix = "ses"

    @classmethod
    def create_whatsapp_session_or_get_whatsapp_session(
        cls, phone_number, stage, position, payload=None
    ):
        whatsapp_session = cls.objects.filter(phone_number=phone_number).first()

        if whatsapp_session:
            logger.info(
                f"Whatsapp session exists: {whatsapp_session}. Updating session"
            )
            cls.update_whatsapp_session(phone_number, stage, position, payload)
            return whatsapp_session
        else:
            whatsapp_session = cls(
                phone_number=phone_number,
                stage=stage,
                position=position,
                payload=payload,
            )
            whatsapp_session.save()

            return whatsapp_session

    @classmethod
    def update_whatsapp_session(cls, phone_number, stage, position, payload):
        whatsapp_session = cls.objects.filter(phone_number=phone_number).update(
            stage=stage, position=position, payload=payload
        )
        return whatsapp_session

    @classmethod
    def get_whatsapp_session(cls, phone_number):
        whatsapp_session = cls.objects.filter(phone_number=phone_number).first()
        return whatsapp_session

    def reset_to_menu(self):
        self.stage = "menu"
        self.position = "menu"
        self.payload = {}
        self.save()
        return self
