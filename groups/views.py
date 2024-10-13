import traceback
from django.shortcuts import render
from rest_framework.views import APIView
from authentication.user_authentication import UserJWTAuthentication
from common.constants import GROUPS_NOT_FOUND, SERIALIZER_IS_NOT_VALID
from exceptions.generic import GenericException
from exceptions.generic_response import GenericSuccessResponse
from groups.models import Groups
from groups.serializers import GroupSerializer

# Create your views here.


class ManageGroup(APIView):
    authentication_classes = [UserJWTAuthentication]

    @staticmethod
    def get(request,group_name):
        try:
            group = Groups.objects.filter(group_name = group_name)
            return GenericSuccessResponse(GroupSerializer(group).data,message = "group fetched successfully" )
        except Groups.DoesNotExist:
            return GenericException(messages=GROUPS_NOT_FOUND)
        except:
            return GenericException()

    @staticmethod    
    def post(request):
        try:
            user = request.user
            request.data["created_by"] = user.user_id
            print(request.data)
            group_serializer = GroupSerializer(data = request.data)
            if group_serializer.is_valid():
                print("valid")
                group = group_serializer.save() 
                return GenericSuccessResponse(GroupSerializer(group),message="group created successfully")
            else:
                print("not valid")
                return GenericException(message=SERIALIZER_IS_NOT_VALID)
        except:
            traceback.print_exc()
            GenericException()

        