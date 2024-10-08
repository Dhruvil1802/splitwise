from rest_framework import serializers
from models import UserAuthTokens


class UserAuthTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAuthTokens
        fields = "__all__"