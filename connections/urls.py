
from django.contrib import admin
from django.urls import path, include

from .views import JoinGroup, ManageConnections, ManageGroup, ManageGroupConnectoins


urlpatterns = [
 
    path("managegroup/<str:group_name>/", ManageGroup.as_view(), name='get_manage_group'),
    path("managegroup/", ManageGroup.as_view(),name='post_manage_group'),
    path("joingroup/",JoinGroup.as_view()),
    path("manageconnections/",ManageConnections.as_view()),
    path("managegroupconnections/<int:group>/",ManageGroupConnectoins.as_view()),
    path("managegroupconnections/",ManageGroupConnectoins.as_view())
    
    
]   
