from rest_framework import serializers

from .models import CustomerOTP, CustomerProfile



class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = "__all__"

class ResetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ["password"]

class OTPVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerOTP
        fields = ["customer_id","otp"]
