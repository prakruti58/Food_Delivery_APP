from django.apps import AppConfig


class CustomerRegConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "customerProfile"

class customSecurityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customSecurity'