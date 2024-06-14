from django.db import models




class CustomerAuthTokens(models.Model):
    class Meta:
        db_table = 'fd_customer_auth_tokens'

    access_token = models.TextField(null=True, db_column="customer_auth_access_token")
    refresh_token = models.TextField(null=True, db_column="customer_auth_refresh_token")
    created_at = models.DateTimeField(auto_now_add=True)
