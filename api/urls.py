from django.urls import path

from api.views.bot.views import WebhookView

urlpatterns = [
    path("bot", WebhookView.as_view(), name="bot"),
]
