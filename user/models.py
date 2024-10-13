from django.db import models

from common.models import Audit

# Create your models here.
    
class Users(Audit):
    class Meta:
        db_table = 'sw_user'

    user_id = models.BigAutoField(primary_key=True)
    user_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

class UserOTP(Audit):
    class Meta:
        db_table = "sw_user_otp"

    user_otp_id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    otp = models.CharField(max_length=255)