from django.db import models



class Audit(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)



class CustomerProfile(models.Model):
    # Define your fields here
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    # Other fields


