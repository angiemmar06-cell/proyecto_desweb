from django.urls import path
from . import views
from rest_framework import routers
from . import views


urlpatterns = [
    path("hello_hidrografia/", views.HelloHidrografia.as_view(),name="hello_hidrografia"),
    path("api/", views.Cauces.as_view(),name="cauces")
]