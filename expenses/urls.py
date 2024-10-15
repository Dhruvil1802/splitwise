
from django.contrib import admin
from django.urls import path, include

from .views import  ManageExpenses, ManageGroupExpenses, SettleExpenses, SettleGroupExpenses, SimplifyGroupExpenses


urlpatterns = [
  
    path("manageexpenses/", ManageExpenses.as_view()),
    path("managegroupexpenses/<str:group>/", ManageGroupExpenses.as_view(), name='get_total_owed_monney'),
    path("managegroupexpenses/",ManageGroupExpenses.as_view()),
    path("settleexpenses/",SettleExpenses.as_view()),
    path("settlegroupexpenses/",SettleGroupExpenses.as_view()),
    path("simplifygroupexpenses/",SimplifyGroupExpenses.as_view()),
    
]   