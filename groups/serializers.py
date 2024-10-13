from rest_framework import serializers
from .models import Groups, GroupMemebers

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groups
        fields = "__all__"

class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMemebers
        fields = "__all__"
        