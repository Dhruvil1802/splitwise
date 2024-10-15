
import operator
import traceback
from django.shortcuts import render
from rest_framework.views import APIView
from authentication.user_authentication import UserJWTAuthentication
from common.constants import BAD_REQUEST, EXPENSE_ADDED_SUCCESSFULLY, EXPENSES_SETTLED_SUCCESSFULLY, GROUP_MEMBERS_LIST_REQUIRED, INCORRECT_USER_EXPENSES, INCORRECT_USER_EXPENSES_PERCENTAGE, INDIVIDUAL_EXPENSE_OF_BOTH_USER_IS_NECESSARY, PERCENTAGE_REQUIRED, SERIALIZER_IS_NOT_VALID, SUCCESSFULLY_FETCHED_TOTAL_OWED_MONEY
from exceptions.generic import CustomBadRequest, GenericException
from exceptions.generic_response import GenericSuccessResponse
from expenses.serializers import ExpenseSerializer, GroupExpenseSerializer
from expenses.models import Expenses, GroupExpenses
from decimal import ROUND_DOWN, Decimal

from connections.models import Connections, GroupConnections, GroupMemebers
from connections.serializers import ConnectionsSerializer, GroupConnectionsSerializer, UpdateOwedMoneyInGroupSerializer, UpdateOwedMoneySerializer
# Create your views here.

class ManageExpenses(APIView):
    authentication_classes = [UserJWTAuthentication]

    # total money user owe
    @staticmethod
    def get(request):
        try:
            connections = Connections.objects.filter(user1 = request.user.user_id).values_list("money_owes",flat=True)
            return GenericSuccessResponse(data={"total_owed_money":sum(connections)},message=SUCCESSFULLY_FETCHED_TOTAL_OWED_MONEY)
        except:
            return GenericException()

    # add expenses
    @staticmethod
    def post(request):
        try:
            user1 = request.user
            request.data["user1"] = user1.user_id

            if "user2" not in request.data or "expense_amount" not in request.data or "distribution_type" not in request.data:
                return CustomBadRequest(message=BAD_REQUEST)
            if request.data["distribution_type"]=="percentage" and "user1_percentage" not in request.data and "user2_percentage" not in request.data:
                return CustomBadRequest(message = PERCENTAGE_REQUIRED)
            if request.data["distribution_type"]=="unequally" and "user2_expense" not in request.data and "user1_expense" not in request.data:
                return CustomBadRequest(message=INDIVIDUAL_EXPENSE_OF_BOTH_USER_IS_NECESSARY)  
                
            

            if request.data["distribution_type"]=="equally":
                money_owes = Decimal(request.data["expense_amount"])/2


            if request.data["distribution_type"]=="unequally":
                if Decimal(request.data['user1_expense']) + Decimal(request.data['user2_expense']) != Decimal(request.data['expense_amount']):
                    return CustomBadRequest(message=INCORRECT_USER_EXPENSES)
                money_owes = Decimal(request.data["user2_expense"])
              

            if request.data["distribution_type"]=="percentage":
                if Decimal(request.data['user1_percentage']) + Decimal(request.data['user2_percentage']) != 100:
                    return CustomBadRequest(message=INCORRECT_USER_EXPENSES_PERCENTAGE)
                money_owes = Decimal(request.data["expense_amount"])*Decimal(request.data["user2_percentage"])/100
            
            request.data["money_owes"] = money_owes.quantize(Decimal('0.00'), rounding=ROUND_DOWN)


            expense = Expenses.objects.filter(user1=request.data["user1"],user2=request.data["user2"]).last()
            connection = Connections.objects.filter(user1=request.data["user1"],user2=request.data["user2"]).last()

            request.data["total_money_owes"] = connection.money_owes + request.data["money_owes"]

            expense_serializer = ExpenseSerializer(data=request.data)
            connection_serializer = UpdateOwedMoneySerializer(data={"money_owes":request.data["total_money_owes"]})

            if expense_serializer.is_valid(raise_exception=True) and connection_serializer.is_valid(raise_exception=True):
                connection = connection_serializer.update(connection,{"money_owes":request.data["total_money_owes"]})
                expense = expense_serializer.save()
                data = {"expense":ExpenseSerializer(expense).data,"connection":UpdateOwedMoneySerializer(connection).data}
                return GenericSuccessResponse(data, message=EXPENSE_ADDED_SUCCESSFULLY)
            
            else:
                return CustomBadRequest(message=SERIALIZER_IS_NOT_VALID)
        except:
            traceback.print_exc()
            return GenericException()

class ManageGroupExpenses(APIView):
    authentication_classes = [UserJWTAuthentication]

    # total money user owe
    @staticmethod
    def get(request,group):
        try:
            connections = GroupConnections.objects.filter(user1 = request.user.user_id,group=group).values_list("money_owes",flat=True)
            return GenericSuccessResponse(data={"total_owed_money":sum(connections)},message=SUCCESSFULLY_FETCHED_TOTAL_OWED_MONEY)
        except:
            traceback.print_exc()
            return GenericException()
        
    # add group expenses
    @staticmethod
    def post(request):
        try:
            user1 = request.user
            request.data["user1"] = user1.user_id
            print("user1",user1.user_id)
            if "expense_amount" not in request.data or "distribution_type" not in request.data or "group" not in request.data:
                return CustomBadRequest(message="dont know")
            if request.data["distribution_type"]=="equally" and "group_members_list" not in request.data:
                return CustomBadRequest(message = GROUP_MEMBERS_LIST_REQUIRED)
            if request.data["distribution_type"]=="percentage" and "percentage_expense_dict" not in request.data:
                return CustomBadRequest(message = PERCENTAGE_REQUIRED)
            if request.data["distribution_type"]=="unequally" and "unequal_expense_dict" not in request.data:
                return CustomBadRequest(message=INDIVIDUAL_EXPENSE_OF_BOTH_USER_IS_NECESSARY)  
                    
            

            if request.data["distribution_type"]=="equally":
               
                money_owes = Decimal(request.data["expense_amount"])/len(request.data["group_members_list"])
                expense_dict = {}

                print(money_owes)
                
                for i in request.data["group_members_list"]:
                    expense_dict[i] = money_owes
              

            if request.data["distribution_type"] == "unequally":
               
                total_money = Decimal(0)
                expense_dict = {}

                print(request.data['unequal_expense_dict'])  

                for user, money_owes in request.data['unequal_expense_dict'].items():
                    expense_dict[user] = Decimal(money_owes) 
                    total_money = total_money + Decimal(money_owes) 

                if total_money != Decimal(request.data["expense_amount"]):
                    return CustomBadRequest(message=INCORRECT_USER_EXPENSES)
                

            if request.data["distribution_type"] == "percentage":
               
                total_money = Decimal(0)
                expense_dict = {}
                expense_amount = request.data["expense_amount"]
              
                print(request.data['percentage_expense_dict'])  

                for user, money_percentage_owes in request.data['percentage_expense_dict'].items():
                    expense_dict[user] = Decimal(money_percentage_owes*expense_amount/100) 
                    total_money = total_money + Decimal(money_percentage_owes*expense_amount/100)  

                if total_money != Decimal(request.data["expense_amount"]):
                    return CustomBadRequest(message=INCORRECT_USER_EXPENSES_PERCENTAGE)
        
            shared_expense = []

            for user2, money_owes in expense_dict.items():

                request.data["user2"] = user2
                request.data["money_owes"] = money_owes.quantize(Decimal('0.00'), rounding=ROUND_DOWN)

                if GroupConnections.objects.filter(group = request.data["group"], user1 = user1, user2 = user2):
                    
                    group_connection = GroupConnections.objects.filter(group = request.data["group"], user1 = user1, user2 = user2)[0]

                    request.data["total_money_owes"] = group_connection.money_owes + request.data["money_owes"]
                    
                    group_expense_serializer = GroupExpenseSerializer(data=request.data)
                    group_connection_serializer = UpdateOwedMoneyInGroupSerializer(data = {"money_owes": request.data["total_money_owes"]})
                   
                    if group_expense_serializer.is_valid(raise_exception=True) and group_connection_serializer.is_valid(raise_exception=True):
                        group_connection = group_connection_serializer.update(group_connection,{"money_owes": request.data["total_money_owes"]})
                        expense = group_expense_serializer.save()
                        shared_expense.append(expense)
                    else:
                        return CustomBadRequest(message=SERIALIZER_IS_NOT_VALID)
            
            return GenericSuccessResponse(GroupExpenseSerializer(shared_expense,many=True).data, message=EXPENSE_ADDED_SUCCESSFULLY)

        except:
            traceback.print_exc()
            return GenericException()



class SettleExpenses(APIView):
    authentication_classes = [UserJWTAuthentication]

    # settle individuall expenses
    @staticmethod
    def patch(request):
        try:
            if "user2" not in request.data:
                return CustomBadRequest(message=BAD_REQUEST)

            user1 = request.user.user_id
            user2 = request.data['user2']
            print(user1, user2)

            connection = Connections.objects.filter(user1=user1, user2=user2).first()


            connection_serializer = UpdateOwedMoneySerializer(connection, data={"money_owes": 0})

            if connection_serializer.is_valid(raise_exception=True):
                settled_connection = connection_serializer.save()  

                return GenericSuccessResponse(UpdateOwedMoneySerializer(settled_connection).data,message=EXPENSES_SETTLED_SUCCESSFULLY)

        except Exception as e:
            traceback.print_exc()
            return GenericException()
        
class SettleGroupExpenses(APIView):
    authentication_classes = [UserJWTAuthentication]

    #settle group expenses
    @staticmethod
    def patch(request):
        try:
            if "user2" not in request.data or "group" not in request.data:
                return CustomBadRequest(message=BAD_REQUEST)

            user1 = request.user.user_id
            user2 = request.data['user2']
            group = request.data['group']

            print(user1, user2)

            group_connection = GroupConnections.objects.filter(user1=user1, user2=user2, group=group).first()

            cgroup_onnection_serializer = UpdateOwedMoneyInGroupSerializer(group_connection, data={"money_owes": 0})

            if cgroup_onnection_serializer.is_valid(raise_exception=True):
                settled_connection = cgroup_onnection_serializer.save()  

                return GenericSuccessResponse(UpdateOwedMoneySerializer(settled_connection).data,message=EXPENSES_SETTLED_SUCCESSFULLY)

        except Exception as e:
            traceback.print_exc()
            return GenericException()
        
class SimplifyGroupExpenses(APIView):
    authentication_classes = [UserJWTAuthentication]
    
    # simplify expenses
    @staticmethod
    def patch(request): 
        try:

            if "group" not in request.data:
                return CustomBadRequest(message=BAD_REQUEST)
            group = request.data["group"]
            group_members = GroupMemebers.objects.filter(group = request.data["group"]).values_list("user")
            
            owed_money_dict = {}
            debt_money_dict = {}
            money_dict = {}
            for member in group_members:
                member = member[0]
                print("gp",member)
                owed_money = GroupConnections.objects.filter(user1 = member,group=group).values_list("money_owes",flat=True)
                debt_money = GroupConnections.objects.filter(user2 = member,group=group).values_list("money_owes",flat=True)
                owed_money_dict[member] = sum(owed_money)
                debt_money_dict[member] = sum(debt_money)
                money_dict[member] = sum(owed_money) - sum(debt_money)


            asc_money_dict = dict(sorted(money_dict.items(), key=operator.itemgetter(1)))
            des_money_dict = dict(sorted(money_dict.items(), key=operator.itemgetter(1),reverse=True))
            print("a",asc_money_dict)
            print("d",des_money_dict)
            final_list =[]
            # for ud,md in des_money_dict.items():
            #     for ua,ma in asc_money_dict.items():
            #         if des_money_dict[ud]!=0 and asc_money_dict[ua]!=0:
            #             if md+ma>0 :
                            
            #                 final_list.append([ud,ua,ma])
                            
            #                 des_money_dict[ud] += asc_money_dict[ua]  
            #                 asc_money_dict[ua]=0
            #                 md = md+ma
            #                 ma=0
            #             else:
            #                 final_list.append([ud,ua,md])
            #                 asc_money_dict[ua] += des_money_dict[ud]
            #                 des_money_dict[ud]=0 
            #                 ma = ma + md
            #                 md=0
            #                 continue
            for ud,md in des_money_dict.items():
                for ua, ma in reversed(list(des_money_dict.items())):
                    if des_money_dict[ud]!=0 and des_money_dict[ua]!=0:
                        if md+ma>0 :
                            
                            final_list.append([ud,ua,ma])
                            
                            des_money_dict[ud] += des_money_dict[ua]  
                            des_money_dict[ua]=0
                            md = md+ma
                            ma=0
                        else:
                            final_list.append([ud,ua,md])
                            des_money_dict[ua] += des_money_dict[ud]
                            des_money_dict[ud]=0 
                            ma = ma + md
                            md=0
                            continue
            print(final_list)
            return GenericSuccessResponse(final_list)
        except:
            traceback.print_exc()
            return GenericException()

