from datetime import timezone
import random
import re
import traceback
from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password

from common.constants import (
     BAD_REQUEST,
     INCORRECT_PASSWORD,
     NEW_PASSWORD_DOESNT_MATCH,
     OTP_DOESNT_MATCH,
     OTP_EXPIRED,
     OTP_SENT_SUCCESSFULLY,
    PASSWORD_LENGTH_SHOULD_BE_BETWEEN_8_TO_20, PASSWORD_MUST_HAVE_ONE_NUMBER,
    PASSWORD_MUST_HAVE_ONE_SMALLERCASE_LETTER, PASSWORD_MUST_HAVE_ONE_SPECIAL_CHARACTER,
    PASSWORD_MUST_HAVE_ONE_UPPERCASE_LETTER,
     SERIALIZER_IS_NOT_VALID,
     USER_ALREADY_EXISTS,
     USER_DOESNT_EXISTS,
     USER_LOGGED_IN_SUCCESSFULLY,
     USER_LOGGED_OUT_SUCCESSFULLY,
     USER_REGISTERED_SUCCESSFULLY,
     YOUR_PASSWORD_UPDATED_SUCCESSFULLY
)


from authentication.user_authentication import UserJWTAuthentication, get_user_authentication_token, save_token

from authentication.models import UserAuthTokens
from exceptions.generic import CustomBadRequest, GenericException
from exceptions.generic_response import GenericSuccessResponse
from rest_framework.views import APIView

from django.db.models import Q

from user.serializers import RegistrationSerializer
from common.views import send_mail, validate_password
from .models import UserOTP, Users
from user.serializers import OTPVerificationSerializer, ResetPasswordSerializer

from rest_framework.views import APIView
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from .serializers import ResetPasswordSerializer
from .models import Users, UserOTP
from exceptions.generic import CustomBadRequest, GenericException


# Create your views here.

class Registration(APIView):
    @staticmethod
    def post(request):
        try:
 
            if not all(key in request.data for key in ["password", "email", "user_name"]):
                return CustomBadRequest(message=BAD_REQUEST)

            password = request.data["password"]
            email = request.data["email"]

            if Users.objects.filter(email=email).exists():
                return CustomBadRequest(message=USER_ALREADY_EXISTS)

            password_validation = validate_password(password)
            if password_validation is not True:
                return password_validation 
            registration_serializer = RegistrationSerializer(data=request.data)

            if registration_serializer.is_valid(raise_exception=True):
                user_instance = registration_serializer.save()
                tokens = get_user_authentication_token(user_instance)
                save_token(tokens)

                return GenericSuccessResponse(tokens, message=USER_REGISTERED_SUCCESSFULLY)

            return CustomBadRequest(message=SERIALIZER_IS_NOT_VALID)

        except Exception:
            return GenericException()
        

class Logout(APIView):
    authentication_classes = [UserJWTAuthentication]

    @staticmethod
    def delete(request):
        try:
            header = request.headers.get("authorization")
            if not header:

                return CustomBadRequest(message="Authorization header missing")

            token = header.split(" ")[1]
            UserAuthTokens.objects.filter(Q(access_token=token) | Q(refresh_token=token)).delete()

            return GenericSuccessResponse(message=USER_LOGGED_OUT_SUCCESSFULLY)
        
        except Exception:
            return GenericException()


class Login(APIView):
    @staticmethod
    def post(request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")

            if not email or not password:
                raise GenericException(message="Email and password are required.")

            if Users.objects.filter(email=email).exists():
                user = Users.objects.get(email=email, is_deleted=False)
            else:
                return CustomBadRequest(message=USER_DOESNT_EXISTS)

            print(password,user.password)
            if password != user.password:
                return CustomBadRequest(message=INCORRECT_PASSWORD)
        
            authentication_tokens = get_user_authentication_token(user)
            save_token(authentication_tokens)
            return GenericSuccessResponse(authentication_tokens, message=USER_LOGGED_IN_SUCCESSFULLY)

        except Users.DoesNotExist:
            raise GenericException(message="Email not found.")
        except Exception:
            return GenericException()


class ResetPassword(APIView):
    
    @staticmethod
    def patch(request):
        try:
            if "email" not in request.data or "new_password" not in request.data or "confirm_password" not in request.data:
                raise CustomBadRequest(message=BAD_REQUEST)
            new_password = request.data["new_password"]
            confirm_password = request.data["confirm_password"]
            email = request.data["email"]
            customer = Users.objects.get(email=email, is_deleted=False)
            if not (check_password == customer.password):
                if new_password == confirm_password:
                    if validate_password(confirm_password):
                        customer.password = make_password(new_password)
                        customer.save()
                        return GenericSuccessResponse('e', message=YOUR_PASSWORD_UPDATED_SUCCESSFULLY)
                else:
                    return CustomBadRequest(message=NEW_PASSWORD_DOESNT_MATCH)
            else:
                return CustomBadRequest(message=INCORRECT_PASSWORD)
        except Exception as e:
            return GenericException()


class OTPVerification(APIView):
    def post(self, request):
        try:
            email = request.data.get("email")
            if not email:
                return GenericException(message="Email not found") 
            otp = str(random.randint(1000, 9999))
            try:
                user = Users.objects.get(email=email, is_deleted=False)
            except Users.DoesNotExist:
                return GenericException(message="user does not exists")
            otp_verification_data = {
                "otp": otp,
                "user_id": user.user_id
            }
            otpverification_serializer = OTPVerificationSerializer(data=otp_verification_data)
            if otpverification_serializer.is_valid():
                otpverification_serializer.save()
                send_mail([email], msg=otp)

                return GenericSuccessResponse('e', message=OTP_SENT_SUCCESSFULLY)
            else:
                return GenericException(message=SERIALIZER_IS_NOT_VALID)
            
        except Exception as e:
            return GenericException()


class ForgotPassword(APIView):
    @staticmethod
    def patch(request):
        try:
            if "email" not in request.data or "new_password" not in request.data or "confirm_password" not in request.data or "otp" not in request.data:
                raise CustomBadRequest(message=BAD_REQUEST)
            new_password = request.data["new_password"]
            confirm_password = request.data["confirm_password"]
            email = request.data["email"]
            otp = request.data["otp"]
            del request.data["new_password"]
            del request.data["confirm_password"]
            del request.data["email"]
            del request.data["otp"]
            resetpassword_serializer = ResetPasswordSerializer(data=request.data)
            user = Users.objects.get(email=email, is_deleted=False)
            user_otp = UserOTP.objects.filter(user_id=user.user_id).last()
            print("user otp", user_otp.created_at)
            if new_password == confirm_password:
                if (timezone.now() - user_otp.created_at < timezone.timedelta(minutes=2)):
                    if user_otp.otp == otp:
                        if validate_password(confirm_password):
                            request.data["password"] = make_password(new_password)
                            if resetpassword_serializer.is_valid():
                                resetpassword_serializer.update(user, resetpassword_serializer.validated_data)
                                return GenericSuccessResponse('e', message=YOUR_PASSWORD_UPDATED_SUCCESSFULLY)
                    else:
                        return CustomBadRequest(message=OTP_DOESNT_MATCH)
                else:
                    return CustomBadRequest(message=OTP_EXPIRED)
            else:
                return CustomBadRequest(message=NEW_PASSWORD_DOESNT_MATCH)
        
        except Exception as e:
            return GenericException()
