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

