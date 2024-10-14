
import traceback
from django.shortcuts import render
from rest_framework.views import APIView
from authentication.user_authentication import UserJWTAuthentication
from common.constants import BAD_REQUEST, EXPENSE_ADDED_SUCCESSFULLY, GROUP_MEMBERS_LIST_REQUIRED, INCORRECT_USER_EXPENSES, INCORRECT_USER_EXPENSES_PERCENTAGE, INDIVIDUAL_EXPENSE_OF_BOTH_USER_IS_NECESSARY, PERCENTAGE_REQUIRED, SERIALIZER_IS_NOT_VALID
from exceptions.generic import CustomBadRequest, GenericException
from exceptions.generic_response import GenericSuccessResponse
from expenses.serializers import ExpenseSerializer
from expenses.models import Expenses
from decimal import ROUND_DOWN, Decimal

from splitwise.connections.models import GroupConnections
# Create your views here.

class ManageExpenses(APIView):
    authentication_classes = [UserJWTAuthentication]

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
            request.data["total_money_owes"] = expense.total_money_owes + request.data["money_owes"]

            expense_serializer = ExpenseSerializer(data=request.data)
            if expense_serializer.is_valid(raise_exception=True):
                
                expense = expense_serializer.save()
                return GenericSuccessResponse(ExpenseSerializer(expense).data, message=EXPENSE_ADDED_SUCCESSFULLY)
            
            else:
                return CustomBadRequest(message=SERIALIZER_IS_NOT_VALID)
        except:
            traceback.print_exc()
            GenericException()

class ManageGroupExpenses(APIView):
    authentication_classes = [UserJWTAuthentication]

    # add group expenses
    @staticmethod
    def post(request):
        try:
            user1 = request.user
            request.data["user1"] = user1.user_id

            if "expense_amount" not in request.data or "distribution_type_in_group" not in request.data or "group" not in request.data:
                return CustomBadRequest(message="dont know")
            if request.data["distribution_type_in_group"]=="equally" and "group_members_list" not in request.data:
                return CustomBadRequest(message = GROUP_MEMBERS_LIST_REQUIRED)
            if request.data["distribution_type_in_group"]=="percentage" and "percentage_list" not in request.data:
                return CustomBadRequest(message = PERCENTAGE_REQUIRED)
            if request.data["distribution_type_in_group"]=="unequally" and "expense_list" not in request.data:
                return CustomBadRequest(message=INDIVIDUAL_EXPENSE_OF_BOTH_USER_IS_NECESSARY)  
                    
            

            if request.data["distribution_type_in_group"]=="equally":
                money_owes = Decimal(request.data["expense_amount"])/len(request.data["group_members_list"])
                print(money_owes)

            # if request.data["distribution_type"]=="unequally":
            #     if Decimal(request.data['user1_expense']) + Decimal(request.data['user2_expense']) != Decimal(request.data['expense_amount']):
            #         return CustomBadRequest(message=INCORRECT_USER_EXPENSES)
            #     money_owes = Decimal(request.data["user2_expense"])
              

            # if request.data["distribution_type"]=="percentage":
            #     if Decimal(request.data['user1_percentage']) + Decimal(request.data['user2_percentage']) != 100:
            #         return CustomBadRequest(message=INCORRECT_USER_EXPENSES_PERCENTAGE)
            #     money_owes = Decimal(request.data["expense_amount"])*Decimal(request.data["user2_percentage"])/100
            
            request.data["money_owes"] = money_owes.quantize(Decimal('0.00'), rounding=ROUND_DOWN)

            for user2 in request.data["group_members_list"]:
                print(user2)
                if GroupConnections.objects.filter(group = request.data["group"], user1 = user1, user2 = user2):
                    
                    # expense = Expenses.objects.filter(user1=request.data["user1"],user2=request.data["user2"]).last()
                    request.data["total_money_owes"] = expense.total_money_owes + request.data["money_owes"]

            expense_serializer = ExpenseSerializer(data=request.data)
            if expense_serializer.is_valid(raise_exception=True):
                
                expense = expense_serializer.save()
                return GenericSuccessResponse(ExpenseSerializer(expense).data, message=EXPENSE_ADDED_SUCCESSFULLY)
            
            else:
                return CustomBadRequest(message=SERIALIZER_IS_NOT_VALID)
        except:
            traceback.print_exc()
            GenericException()

