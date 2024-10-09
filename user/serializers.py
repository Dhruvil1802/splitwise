from rest_framework import serializers
from .models import UserOTP, Users

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = "__all__"

class OTPVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOTP
        fields = ["user_id","otp"]

class ResetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["password"]
    
