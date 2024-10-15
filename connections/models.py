from django.db import models

from common.models import Audit
from user.models import Users

# Create your models here.
    
class Groups(Audit):
    class Meta:
        db_table = 'sw_groups'

    group_id = models.BigAutoField(primary_key=True)
    group_name = models.CharField(max_length=255)
    created_by = models.ForeignKey(Users,on_delete=models.CASCADE)

class GroupMemebers(Audit):
    class Meta:
        db_table = 'sw_group_members'

    group_memeber_id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(Groups,on_delete=models.CASCADE)
    user = models.ForeignKey(Users,on_delete=models.CASCADE)

class Connections(Audit):
    class Meta:
        db_table = 'sw_connections'
        
    connection_id = models.BigAutoField(primary_key=True)
    user1 = models.ForeignKey(Users,on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(Users,on_delete=models.CASCADE, related_name='user2')
    money_owes = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class GroupConnections(Audit):
    class Meta:
        db_table = 'sw_group_connections'
        
    group_connection_id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(Groups,on_delete=models.CASCADE, related_name="group")
    user1 = models.ForeignKey(Users,on_delete=models.CASCADE, related_name='group_user1')
    user2 = models.ForeignKey(Users,on_delete=models.CASCADE, related_name='group_user2')
    money_owes = models.DecimalField(max_digits=10, decimal_places=2, default=0)