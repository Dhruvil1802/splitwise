from django.db import models

class UserAuthTokens(models.Model):
    class Meta:
        db_table = 'sw_user_auth_tokens'

    access_token = models.TextField(null=True, db_column="auth_access_token")
    refresh_token = models.TextField(null=True, db_column="auth_refresh_token")
    created_at = models.DateTimeField(auto_now_add=True)