import json

from django.db import models
from django.contrib.auth.models import AbstractUser

from users.managers import UserManager
from mboma.model import EnumModel
from django.utils.translation import gettext_lazy as _
from loguru import logger
from django.contrib.auth.hashers import make_password, check_password
from services.helpers.readable_date import readable_date_time_string
from django.utils import timezone


class UserRoles(EnumModel):
    ADMIN = "ADMIN", _("ADMIN")
    CUSTOMER = "CUSTOMER", _("CUSTOMER")


class User(AbstractUser):
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=UserRoles.choices,
    )
    source = models.CharField(max_length=255, blank=True, null=True)
    is_registered = models.BooleanField(default=False)
    has_session = models.BooleanField(default=False)
    password_history = models.TextField(blank=True, null=True, editable=False)
    password_updated_at = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    class Meta:
        ordering = ["last_name"]
        verbose_name = "User"
        verbose_name_plural = "Users"
        table_prefix = "user"

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "phone_number"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def create_user(
        cls,
        username,
        first_name,
        last_name,
        email,
        phone_number,
        role,
        source="manual",
        password=None,
        **kwargs,
    ):
        password = f"{first_name}{last_name}" if password is None else password
        user = cls(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            role=role,
            source=source,
            **kwargs,
        )
        user.set_password(password)
        user.save()
        return user

    @classmethod
    def get_user_by_phone_number(cls, phone_number):
        user = cls.objects.filter(phone_number=phone_number).first()
        return user

    def update_registration(self, data):
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.email = data("email_address")
        self.is_registered = True
        self.save()

    def set_password(self, raw_password):
        try:
            if self.password_history is not None:
                password_history = json.loads(self.password_history)
            else:
                password_history = []
            for password_json in password_history:
                logger.debug(f"password_json: {password_json}")
                password_object = json.loads(password_json)
                logger.debug(f"password_object: {password_object}")

                if check_password(
                    password=raw_password,
                    encoded=password_object.get("password"),
                    setter=None,
                ):
                    password_changed_on = password_object.get("changed_on")
                    password_changed_on_readable_date = readable_date_time_string(
                        date=password_changed_on
                    )
                    raise Exception(
                        f"This password was used before and was changed on "
                        f"{password_changed_on_readable_date[0]} around {password_changed_on_readable_date[1]}."
                    )

            # Add previous password to history list
            logger.debug(f"changing password right now: {timezone.now()}")
            password_history.append(
                json.dumps(
                    {"password": self.password, "changed_on": str(timezone.now())}
                )
            )

            self.password_history = json.dumps(password_history)
            self.password = make_password(raw_password)
            self._password = raw_password
            self.password_updated_at = timezone.now()
        except Exception as exc:
            logger.error(f"exception setting password: {exc}")
            raise

    def save(self, *args, **kwargs):
        # set admin user permissions
        if self.is_superuser:
            self.role = UserRoles.ADMIN
            self.is_verified = True
        super().save(*args, **kwargs)
