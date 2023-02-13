from django.db import models

from mboma.model import SoftDeleteModel
from loguru import logger


class WhatsappSession(SoftDeleteModel):
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    dialog_name = models.CharField(max_length=255, blank=True, null=True)
    stage = models.CharField(max_length=255, blank=True, null=True)
    payload = models.JSONField(blank=False, null=False, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.phone_number} | {self.stage} | {self.payload} | {self.dialog_name}"
        )

    class Meta:
        db_table = "whatsapp_sessions"
        verbose_name = "Whatsapp Session"
        verbose_name_plural = "Whatsapp Sessions"
        table_prefix = "ses"

    @classmethod
    def create_whatsapp_session_or_get_whatsapp_session(cls, phone_number):
        session = cls.objects.filter(phone_number=phone_number).first()

        if session:
            logger.info(f"session exists --> {session}")
            return session
        else:
            session = cls(
                phone_number=phone_number,
            )
            session.save()

            return session

    @classmethod
    def update_whatsapp_session(cls, phone_number, dialog_name, payload):
        whatsapp_session = cls.objects.filter(phone_number=phone_number).update(
            dialog_name, payload=payload
        )
        return whatsapp_session

    @classmethod
    def get_whatsapp_session(cls, phone_number):
        whatsapp_session = cls.objects.filter(phone_number=phone_number).first()
        return whatsapp_session

    def reset_to_menu(self):
        self.dialog_name = None
        self.payload = {}
        self.save()
        return self
