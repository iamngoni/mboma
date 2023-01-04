from rest_framework import serializers


class IncomingMessageSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    from_me = serializers.BooleanField(required=True)
    timestamp = serializers.DateTimeField()
    id = serializers.CharField()
    chat_id = serializers.CharField(required=True)

    def create(self, validated_data):
        return super().create(validated_data)
