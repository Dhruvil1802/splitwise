from rest_framework import serializers
from .models import Connections, GroupConnections, Groups, GroupMemebers

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groups
        fields = "__all__"

class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMemebers
        fields = "__all__"
        
class ConnectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connections
        fields = "__all__"

class GroupConnectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupConnections
        fields = "__all__"

class UpdateOwedMoneyInGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupConnections
        fields = ['money_owes']

class UpdateOwedMoneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Connections
        fields = ['money_owes']