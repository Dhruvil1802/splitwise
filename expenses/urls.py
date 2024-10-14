
from django.contrib import admin
from django.urls import path, include

from .views import  ManageExpenses, ManageGroupExpenses


urlpatterns = [
  
    path("manageexpenses/", ManageExpenses.as_view()),
    path("managegroupexpenses/",ManageGroupExpenses.as_view())

]   