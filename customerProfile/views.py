import datetime
import smtplib
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pytz # type: ignore
from customSecurity.customerAuthorization import CustomerJWTAuthentication, CustomerJWTAuthentication, get_authentication_tokens, save_auth_tokens
from customSecurity.models import CustomerAuthTokens

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import re

from .helpers import validate_password
from .helpers import send_mail
from .models import CustomerOTP, CustomerProfile
from .serializers import RegistrationSerializer, ResetPasswordSerializer, OTPVerificationSerializer
from django.contrib.auth.hashers import make_password, check_password
from common.exceptions import BadRequest, GenericException, CustomBadRequest
from common.genericResponse import GenericSuccessResponse
#from custom_security.authorization import get_authentication_tokens, save_auth_tokens, EmployeeJWTAuthentication
from common.messages import BAD_REQUEST, EMAIL_ALREADY_EXISTS, INCORRECT_PASSWORD, NEW_PASSWORD_DOESNT_MATCH, OTP_DOESNT_MATCH, OTP_EXPIRED, OTP_SENT_SUCCESSFULLY, USER_LOGGED_IN_SUCCESSFULLY, USER_LOGGED_OUT_SUCCESSFULLY, USER_REGISTERED_SUCCESSFULLY, WRONG_EMAIL, YOUR_PASSWORD_UPDATED_SUCCESSFULLY
# BAD_REQUEST, EMAIL_ALREADY_EXISTS, \
#     USER_LOGGED_OUT_SUCCESSFULLY, USER_LOGGED_IN_SUCCESSFULLY, INCORRECT_PASSWORD, WRONG_EMAIL, \
#     PASSWORD_LENGTH_SHOULD_BE_BETWEEN_8_TO_20, PASSWORD_MUST_HAVE_ONE_NUMBER, PASSWORD_MUST_HAVE_ONE_SMALLERCASE_LETTER, \
#     PASSWORD_MUST_HAVE_ONE_UPPERCASE_LETTER, PASSWORD_MUST_HAVE_ONE_SPECIAL_CHARACTER, USER_LOGGED_OUT_SUCCESSFULLY, \
#     USER_LOGGED_IN_SUCCESSFULLY, INCORRECT_PASSWORD, WRONG_EMAIL, PASSWORD_LENGTH_SHOULD_BE_BETWEEN_8_TO_20, \
#     PASSWORD_MUST_HAVE_ONE_NUMBER, PASSWORD_MUST_HAVE_ONE_SMALLERCASE_LETTER, PASSWORD_MUST_HAVE_ONE_UPPERCASE_LETTER, \
#     PASSWORD_MUST_HAVE_ONE_SPEACIAL_CHARACTER, YOUR_PASSWORD_UPDATED_SUCCESSFULLY, NEW_PASSWORD_DOESNT_MATCH, \
#     OTP_SENT_SUCCESSFULLY, OTP_SENT_SUCCESSFULLY_TO_YOUR_EMAIL_ID, OTP_DOESNT_MATCH
# from administrator.models import Holidays
# from custom_security.models import AuthTokens
import random


class Registration(APIView):

    @staticmethod
    def post(request):
        try:
            registration_serializer = RegistrationSerializer(data=request.data)

            if "password" in request.data:
                if validate_password(request.data["password"]):
                    request.data["password"] = make_password(request.data["password"])

            if "email" in request.data and CustomerProfile.objects.filter(email=request.data["email"],
                                                                    is_deleted=False).exists():
                return CustomBadRequest(message=EMAIL_ALREADY_EXISTS)

            if registration_serializer.is_valid():
                customer = registration_serializer.save()

                authentication_tokens = get_authentication_tokens(customer)
                save_auth_tokens(authentication_tokens)

                return GenericSuccessResponse(authentication_tokens, message=USER_REGISTERED_SUCCESSFULLY)
                
            else:
                return CustomBadRequest(message=BAD_REQUEST)

        except Exception as e:
            traceback.print_exc(e)
            return GenericException()
        
class Logout(APIView):
    authentication_classes = [CustomerJWTAuthentication]

    @staticmethod
    def post(request):
        try:
            token = request.headers.get("authorization").split(" ")[1]
            CustomerAuthTokens.objects.filter(access_token=token).delete()

            return GenericSuccessResponse(message=USER_LOGGED_OUT_SUCCESSFULLY)
        except Exception as e:
            return GenericException()


class Login(APIView):
    @staticmethod
    def post(request):
        try:
            if "email" not in request.data or "password" not in request.data:
                raise CustomBadRequest(message=BAD_REQUEST)

            customer = CustomerProfile.objects.get(email=request.data["email"],
                                             is_deleted=False)

            if check_password(request.data["password"], customer.password):
                authentication_tokens = get_authentication_tokens(customer)
                save_auth_tokens(authentication_tokens)
                return GenericSuccessResponse(authentication_tokens, message=USER_LOGGED_IN_SUCCESSFULLY)
            else:
                return CustomBadRequest(message=INCORRECT_PASSWORD)

        except CustomerProfile.DoesNotExist:
            return CustomBadRequest(message=WRONG_EMAIL)
        except Exception as e:
            return GenericException()
        
class ResetPassword(APIView):
    @staticmethod
    def patch(request):
        try:
            if "email" not in request.data or "new_password1" not in request.data or "new_password2" not in request.data:
                raise CustomBadRequest(message=BAD_REQUEST)
            new_password1 = request.data["new_password1"]
            new_password2 = request.data["new_password2"]
            email = request.data["email"]
            del request.data["new_password1"]
            del request.data["new_password2"]
            del request.data["email"]

            resetpassword_serializer = ResetPasswordSerializer(data = request.data)
            if "password" not in request.data:
                raise CustomBadRequest(message=BAD_REQUEST)
            else:
                customer = CustomerProfile.objects.get(email=email, is_deleted = False)
                if check_password(request.data["password"],customer.password):
                    if new_password1 == new_password2:
                        if validate_password(new_password2):
                            request.data["password"] = make_password(new_password1)
                            if resetpassword_serializer.is_valid():
                                resetpassword_serializer.update(customer,resetpassword_serializer.validated_data)
                                return GenericSuccessResponse('e', message=YOUR_PASSWORD_UPDATED_SUCCESSFULLY)
                    else:
                        return CustomBadRequest(message=NEW_PASSWORD_DOESNT_MATCH)
                else:
                    return CustomBadRequest(message=INCORRECT_PASSWORD)

        except Exception as e:
            return GenericException(traceback)

class OTPVerification(APIView):
    @staticmethod
    def post(request):
        try:
            if "email" not in request.data:
                raise CustomBadRequest(message=BAD_REQUEST)
            email = request.data["email"]
            otp = str(random.randint(1000, 9999))
            request.data["otp"] = otp
            del request.data["email"]

            customer = CustomerProfile.objects.get(email=email, is_deleted=False)
            request.data["customer_id"] = customer.customer_id
            otpverification_serializer = OTPVerificationSerializer(data = request.data)

            if otpverification_serializer.is_valid():
                otpverification_serializer.save()
                send_mail([email], msg=otp)
                return GenericSuccessResponse("e", message=OTP_SENT_SUCCESSFULLY)
            

        except CustomerProfile.DoesNotExist:
            return CustomBadRequest(message=WRONG_EMAIL)
        except Exception as e:
            # traceback.print_exc(e)
            return GenericException()


class ForgotPassword(APIView):
    @staticmethod
    def patch(request):
        try:
            if "email" not in request.data or "new_password1" not in request.data or "new_password2" not in request.data or "otp" not in request.data:
               raise CustomBadRequest(message=BAD_REQUEST)
            new_password1 = request.data["new_password1"]
            new_password2 = request.data["new_password2"]
            email = request.data["email"]
            otp = request.data["otp"]
            del request.data["new_password1"]
            del request.data["new_password2"]
            del request.data["email"]
            del request.data["otp"]

            resetpassword_serializer = ResetPasswordSerializer(data = request.data)
            customer = CustomerProfile.objects.get(email=email, is_deleted = False)
            customer_otp = CustomerOTP.objects.filter(customer_id = customer.customer_id).last()
            print("customer otp",customer_otp.created_at)
            if new_password1 == new_password2:
                if(datetime.datetime.now(pytz.UTC) - customer_otp.created_at < datetime.timedelta(minutes=2)):
                    if customer_otp.otp == otp:
                        if validate_password(new_password2):
                            request.data["password"] = make_password(new_password1)
                            if resetpassword_serializer.is_valid():
                                resetpassword_serializer.update(customer,resetpassword_serializer.validated_data)
                                return GenericSuccessResponse('e', message=YOUR_PASSWORD_UPDATED_SUCCESSFULLY)
                    else:
                        return CustomBadRequest(message=OTP_DOESNT_MATCH)
                else:
                    return CustomBadRequest(message=OTP_EXPIRED)
            else:
                return CustomBadRequest(message=NEW_PASSWORD_DOESNT_MATCH)
              
        except Exception as e:
            return GenericException()
        


    