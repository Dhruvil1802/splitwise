
from django.contrib import admin
from django.urls import path, include

from groups.views import JoinGroup, ManageGroup


urlpatterns = [
 
    path("managegroup/", ManageGroup.as_view()),
    path("joingroup/",JoinGroup.as_view())
]
