from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": "User with specified credentials not found",
    }


class ResponseCustomTokenObtainPairSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()


class TokenBlacklistSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        default="",
        help_text="Should be empty string",
    )
