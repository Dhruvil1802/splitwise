import datetime
from django.db.models import Q
from user.models import Users

from common.constants import TOKEN_IS_EXPIRED
from .serializers import UserAuthTokenSerializer
from exceptions.generic import CustomBadRequest, GenericException
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
from splitwise import settings

from .models import UserAuthTokens



def get_user_authentication_token(user):

    user_refresh_token = jwt.encode(
        payload={
            "token_type": "refresh",
            "user_id": user.user_id,
            "email": user.email,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + settings.REFRESH_TOKEN_LIFETIME
        }, 
        key=settings.JWT_SECRET, 
        algorithm=settings.JWT_ALGORITHM
    )

    user_access_token = jwt.encode(
        payload={
            "token_type": "access",
            "user_id": user.user_id,
            "email": user.email,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + settings.ACCESS_TOKEN_LIFETIME
        }, 
        key=settings.JWT_SECRET, 
        algorithm=settings.JWT_ALGORITHM
    )

    return {"user_access_token":user_access_token , "user_refresh_token":user_refresh_token}

def save_token(token):
    
    user_auth_token_serializer = UserAuthTokenSerializer(data={"access_token": token["user_access_token"],"refresh_token":token["user_refresh_token"]})

    if user_auth_token_serializer.is_valid():
        user_auth_token_serializer.save()
    else:
        print("Token serializer errors:", user_auth_token_serializer.errors)



class UserJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        try:
            header = request.headers.get("authorization")
            if not header:
                return CustomBadRequest(message="Authorization header missing")
            user_token = header.split(" ")[1]
            print(user_token)

            if not UserAuthTokens.objects.filter(Q(access_token=user_token) | Q(refresh_token=user_token)).exists():
                return CustomBadRequest(message=TOKEN_IS_EXPIRED)

        
            claims = jwt.decode(user_token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            print("claims", claims)
            user = Users.objects.get(user_id=claims["user_id"], email=claims["email"], is_deleted=False)
            print("user here", user)

            return user, claims
        
        except Users.DoesNotExist:
            raise AuthenticationFailed("User does not exist")
        except:
            GenericException()
        
