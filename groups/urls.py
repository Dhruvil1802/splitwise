
from django.contrib import admin
from django.urls import path, include

from groups.views import ManageGroup


urlpatterns = [
 
    path("managegroup/", ManageGroup.as_view()),

]
