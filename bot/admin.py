from django.contrib import admin

from bot.models import WhatsappSession


@admin.register(WhatsappSession)
class UniversalAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]
