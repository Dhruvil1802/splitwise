import traceback
from venv import logger
from django.shortcuts import render
from rest_framework.views import APIView
from authentication.user_authentication import UserJWTAuthentication
from common.constants import GROUP_ALREADY_EXISTS, GROUP_CREATED_SUCCESSFULLY, GROUP_NOT_FOUND, SERIALIZER_IS_NOT_VALID, USER_ADDED_SUCCESSFULLY_IN_THE_GROUP, USER_IS_ALREADY_IN_THE_GROUP
from exceptions.generic import CustomBadRequest, GenericException
from exceptions.generic_response import GenericSuccessResponse
from groups.models import GroupMemebers, Groups
from groups.serializers import GroupMemberSerializer, GroupSerializer
from user.models import Users

# function which can add user in the group
def adduser(user, group):
    print("add userrrrrrrrrrrrrr")
    if GroupMemebers.objects.filter(user = user.user_id , group = group.group_id).exists():
        return CustomBadRequest(message=USER_IS_ALREADY_IN_THE_GROUP)

    group_member = {
                    'group':group.group_id, 
                    'user':user.user_id
                    }
    
    group_member_serializer = GroupMemberSerializer(data = group_member)

    if group_member_serializer.is_valid():

        group_member = group_member_serializer.save()

        return GenericSuccessResponse(GroupMemberSerializer(group_member).data,message=USER_ADDED_SUCCESSFULLY_IN_THE_GROUP)
    
    else:
        return GenericException(message=SERIALIZER_IS_NOT_VALID)


class ManageGroup(APIView):
    authentication_classes = [UserJWTAuthentication]
    
    # search for the group
    @staticmethod
    def get(request,group_name):

        try:
            group = Groups.objects.filter(group_name = group_name)
            return GenericSuccessResponse(GroupSerializer(group).data,message = "group fetched successfully" )
        
        except Groups.DoesNotExist:
            return CustomBadRequest(messages=GROUP_NOT_FOUND)
        
        except:
            return GenericException()

    # create group
    @staticmethod    
    def post(request):
        try:
            user = request.user
            request.data["created_by"] = user.user_id
            
            if Groups.objects.filter(group_name = request.data['group_name']).exists():
                return CustomBadRequest(message=GROUP_ALREADY_EXISTS)
            
            group_serializer = GroupSerializer(data = request.data)

            if group_serializer.is_valid():
                group = group_serializer.save() 
                print("going to add user")
                adduser(user, group)

                return GenericSuccessResponse(GroupSerializer(group).data, message=GROUP_CREATED_SUCCESSFULLY)
            
            else:
                return CustomBadRequest(message=SERIALIZER_IS_NOT_VALID)
            
        except Groups.DoesNotExist:
            return CustomBadRequest(messages=GROUP_NOT_FOUND)
        
        except:
            traceback.print_exc()
            GenericException()

class JoinGroup(APIView):

    authentication_classes = [UserJWTAuthentication]

    # join group
    @staticmethod
    def post(request):
        try:
            user = request.user
            request.data["user"] = user.user_id
            print(request.data["group_id"])
            if Groups.objects.filter(group_id = request.data['group_id']).exists():
                print("1111111")
                group = Groups.objects.filter(group_id = request.data['group_id'])[0]
                print("1111111",group)
                adduser(user, group)
                return GenericSuccessResponse(GroupSerializer(group).data, message=USER_ADDED_SUCCESSFULLY_IN_THE_GROUP)

        except Groups.DoesNotExist:
            return CustomBadRequest(messages=GROUP_NOT_FOUND)
        
        except:
            traceback.print_exc()
            GenericException()

