import traceback
from django.shortcuts import render
from rest_framework.views import APIView
from authentication.user_authentication import UserJWTAuthentication
from common.constants import BAD_REQUEST, CONNECTION_ALREADY_EXISTS, CONNECTION_CREATED_SUCCESSFULLY, CONNECTION_NOT_FOUND, GROUP_ALREADY_EXISTS, GROUP_CREATED_SUCCESSFULLY, GROUP_FETCHED_SUCCESSSFULLY, GROUP_NOT_FOUND, GROUPMEMBER_NOT_FOUND, JOINED_GROUP_SUCCESSFULLY, SERIALIZER_IS_NOT_VALID, SUCCESSFULLY_FETCHED_CONNECTIONS, USER_ADDED_SUCCESSFULLY_IN_THE_GROUP, USER_IS_ALREADY_IN_THE_GROUP, YOU_ALREADY_JOINED_THE_GROUP
from exceptions.generic import CustomBadRequest, GenericException
from exceptions.generic_response import GenericSuccessResponse
from connections.models import Connections, GroupConnections, GroupMemebers, Groups
from connections.serializers import ConnectionsSerializer, GroupConnectionsSerializer, GroupMemberSerializer, GroupSerializer
from user.models import Users

# function which can add user in the group
def adduser(user, group):
    
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
    
            if Groups.objects.filter(group_name = group_name):
                group = Groups.objects.filter(group_name = group_name)[0]
            else:
                return CustomBadRequest(message=GROUP_NOT_FOUND)

            return GenericSuccessResponse(GroupSerializer(group).data, message = GROUP_FETCHED_SUCCESSSFULLY )
        
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
                
                adduser(user, group)

                return GenericSuccessResponse(GroupSerializer(group).data, message=GROUP_CREATED_SUCCESSFULLY)
            
            else:
                return CustomBadRequest(message=SERIALIZER_IS_NOT_VALID)
            
        except Groups.DoesNotExist:
            return CustomBadRequest(messages=GROUP_NOT_FOUND)
        
        except:
            return GenericException()

class JoinGroup(APIView):

    authentication_classes = [UserJWTAuthentication]

    # join group
    @staticmethod
    def post(request):
        try:
            user = request.user
            request.data["user2"] = user.user_id
            
            if "group" not in request.data:
                return CustomBadRequest(message=BAD_REQUEST)

            if not Groups.objects.filter(group_id=request.data['group']).exists():
                return CustomBadRequest(message=GROUP_NOT_FOUND)
        
            group_members = GroupMemebers.objects.filter(group = request.data["group"])

            if GroupMemebers.objects.filter(group =request.data["group"], user = user.user_id):
                return CustomBadRequest(message=YOU_ALREADY_JOINED_THE_GROUP)
        
            group = Groups.objects.filter(group_id = request.data['group'])[0]
            adduser(user, group)

            
            c = []
            for user in group_members:
    
                request.data['user1'] = user.user_id
                if GroupConnections.objects.filter(user1 = request.data["user1"], user2 = request.data["user2"], group = request.data['group']):
                    continue
                
                connection1_serializer = GroupConnectionsSerializer(data = request.data)
                connection2_serializer = GroupConnectionsSerializer(data = {"user1":request.data["user2"],"user2":request.data["user1"],"group":request.data["group"]})
                
                if connection1_serializer.is_valid(raise_exception=True) and connection2_serializer.is_valid(raise_exception=True):
                    connection1 = connection1_serializer.save()
                    connection2 = connection2_serializer.save()
                    c.append(connection1)
                    c.append(connection2)
                    
                else:
                    return CustomBadRequest(message=SERIALIZER_IS_NOT_VALID)
                
            return GenericSuccessResponse(ConnectionsSerializer(c, many=True).data, message=JOINED_GROUP_SUCCESSFULLY)
       
        except Groups.DoesNotExist:
            return CustomBadRequest(messages=GROUP_NOT_FOUND)
        except:
            return GenericException()

class ManageGroupConnectoins(APIView):
    authentication_classes = [UserJWTAuthentication]

    # get all connections
    @staticmethod
    def get(request,group):
        try:
            connections = GroupConnections.objects.filter(user1=request.user.user_id, group = group)
            if not connections.exists():
                return CustomBadRequest(message="connections not found")
            return GenericSuccessResponse(GroupConnectionsSerializer(connections, many=True).data, message=SUCCESSFULLY_FETCHED_CONNECTIONS)
        except Exception as e:
            return GenericException()
        
    # add user in the group
    @staticmethod
    def post(request):
        try:

            if "user2" not in request.data or "group" not in request.data:
                return CustomBadRequest(message=BAD_REQUEST)
            
            if not Groups.objects.filter(group_id=request.data['group']).exists():
                return CustomBadRequest(message=GROUP_NOT_FOUND)
            
            user1 = request.user
            request.data["user1"] = user1.user_id
            
            if GroupMemebers.objects.filter(group = request.data["group"], user = request.data["user2"]):
                return CustomBadRequest(message=USER_IS_ALREADY_IN_THE_GROUP)

            group_members = GroupMemebers.objects.filter(group = request.data["group"])

            if Users.objects.filter(user_id = request.data["user2"]).exists():
                group = Groups.objects.filter(group_id = request.data['group'])[0]
                user2 = Users.objects.filter(user_id = request.data["user2"])[0]
                adduser(user2, group)
            
            c = []
            for user in group_members:
             
                request.data['user1'] = user.user_id
                if GroupConnections.objects.filter(user1 = request.data["user1"], user2 = request.data["user2"], group=request.data['group'] ):
                    continue
                
                connection1_serializer = GroupConnectionsSerializer(data = request.data)
                connection2_serializer = GroupConnectionsSerializer(data = {"user1":request.data["user2"],"user2":request.data["user1"],"group":request.data["group"]})
                
                if connection1_serializer.is_valid(raise_exception=True) and connection2_serializer.is_valid(raise_exception=True):
                    connection1 = connection1_serializer.save()
                    connection2 = connection2_serializer.save()
                    c.append(connection1)
                    c.append(connection2)
                    
                else:
                    return CustomBadRequest(message=SERIALIZER_IS_NOT_VALID)
                
            return GenericSuccessResponse(ConnectionsSerializer(c, many=True).data, message=USER_ADDED_SUCCESSFULLY_IN_THE_GROUP)

        except Groups.DoesNotExist:
            return CustomBadRequest(messages=GROUP_NOT_FOUND)
        except GroupMemebers.DoesNotExist:
            return CustomBadRequest(messages=GROUPMEMBER_NOT_FOUND)
        except Connections.DoesNotExist:
            return CustomBadRequest(messages=CONNECTION_NOT_FOUND)
        except:
            return GenericException()


class ManageConnections(APIView):
    authentication_classes = [UserJWTAuthentication]


    # get all connections
    @staticmethod
    def get(request):
        try:
            connections = Connections.objects.filter(user1=request.user.user_id)
            if not connections.exists():
                return CustomBadRequest(message="connections not found")
            return GenericSuccessResponse(ConnectionsSerializer(connections, many=True).data, message=SUCCESSFULLY_FETCHED_CONNECTIONS)
        except Exception as e:
            return GenericException()
   
    # create connections
    @staticmethod
    def post(request):
        try:
            if "user2" not in request.data or request.data["user2"] == "":
                return CustomBadRequest(message=BAD_REQUEST)

            user1 = request.user
            request.data["user1"] = user1.user_id

            if Users.objects.filter(user_id = request.data["user2"]):
                user2 = Users.objects.filter(user_id = request.data["user2"])[0]
                request.data['user2'] = user2.user_id

            if Connections.objects.filter(user1 = request.data["user1"], user2 = request.data["user2"]):
                return CustomBadRequest(message=CONNECTION_ALREADY_EXISTS)
            
            connection1_serializer = ConnectionsSerializer(data = request.data)
            connection2_serializer = ConnectionsSerializer(data = {"user1":request.data["user2"],"user2":request.data["user1"]})
           
            if connection1_serializer.is_valid() and connection2_serializer.is_valid():
                connection1 = connection1_serializer.save()
                connection2 = connection2_serializer.save()
                return GenericSuccessResponse(ConnectionsSerializer([connection1,connection2], many=True).data, message=CONNECTION_CREATED_SUCCESSFULLY)
            
        except:
            return GenericException()
 