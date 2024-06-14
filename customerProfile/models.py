
from django.db import models
from common.models import Audit  # type: ignore

class CustomerProfile(Audit):
    class Meta:
        db_table = "fd_customer_Profile"

    customer_id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255)


class CustomerOTP(Audit):
    class Meta:
        db_table = "ec_customer_otp"

    customer_otp_id = models.BigAutoField(primary_key=True)
    customer_id = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    otp = models.CharField(max_length=255)