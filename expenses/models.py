from enum import Enum
from django.db import models

from common.models import Audit
from connections.models import Groups
from user.models import Users

# Create your models here.
class ExpenseDistributionType(Enum):
    PERCENTAGE = "percentage"
    EQUALLY = "equally"
    UNEQUALLY = "unequally"
    
    @classmethod
    def choices(cls):
        return [(type.value, type.name) for type in cls]


class Expenses(Audit):
    class Meta:
        db_table = 'sw_expenses'

    expense_id = models.BigAutoField(primary_key=True)
    user1 = models.ForeignKey(Users,on_delete=models.CASCADE, related_name='user_expense1') 
    user2 = models.ForeignKey(Users,on_delete=models.CASCADE, related_name='user_expense2')
    money_owes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    distribution_type = models.CharField(choices=ExpenseDistributionType.choices(), max_length=255,null=True)
    total_money_owes = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255,default=None,null=True)

    

class GroupExpenses(Audit):
    class Meta:
        db_table = 'sw_group_expenses'

    expense_id = models.BigAutoField(primary_key=True)
    user1 = models.ForeignKey(Users,on_delete=models.CASCADE, related_name='user1_in_group') 
    user2 = models.ForeignKey(Users,on_delete=models.CASCADE, related_name='user2_in_group')
    group = models.ForeignKey(Groups,on_delete=models.CASCADE, related_name="this_group")
    money_owes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.CharField(max_length=255,default=None,null=True)
    distribution_type = models.CharField(choices=ExpenseDistributionType.choices(), max_length=255,null=True)
    total_money_owes = models.DecimalField(max_digits=10, decimal_places=2)