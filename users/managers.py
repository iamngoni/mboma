from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_superuser(self, username, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)
        other_fields.setdefault("role", "ADMIN")

        if other_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be assigned to is_staff=True.")
        if other_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True.")
        return self.create_user(username, password, **other_fields)

    def create_user(self, username, password, **other_fields):
        #     if not username:
        #         raise ValueError("You must provide username")
        #     usr = self.model(username=username, **other_fields)

        return self.model.create_user(
            username=username, password=password, **other_fields
        )
