from rest_framework import serializers
from expenses.models import Expenses, GroupExpenses

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expenses
        fields= "__all__"

class GroupExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupExpenses
        fields= "__all__"