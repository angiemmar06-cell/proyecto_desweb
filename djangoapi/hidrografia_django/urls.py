from django.urls import path
from . import views
from rest_framework import routers
from . import views


urlpatterns = [
    # Cauces
    path("cauces/selectall/", views.cauces_select_all, name="cauces_select_all"),
    path("cauces/selectone/<int:id>/", views.cauces_select_one, name="cauces_select_one"),
    path("cauces/insert/", views.cauces_insert, name="cauces_insert"),
    path("cauces/update/<int:id>/", views.cauces_update, name="cauces_update"),
    path("cauces/delete/<int:id>/", views.cauces_delete, name="cauces_delete"),

    # Estaciones
    path("estaciones/selectall/", views.estaciones_select_all, name="estaciones_select_all"),
    path("estaciones/selectone/<int:id>/", views.estaciones_select_one, name="estaciones_select_one"),
    path("estaciones/insert/", views.estaciones_insert, name="estaciones_insert"),
    path("estaciones/update/<int:id>/", views.estaciones_update, name="estaciones_update"),
    path("estaciones/delete/<int:id>/", views.estaciones_delete, name="estaciones_delete"),

    # Subcuencas
    path("subcuencas/selectall/", views.subcuencas_select_all, name="subcuencas_select_all"),
    path("subcuencas/selectone/<int:id>/", views.subcuencas_select_one, name="subcuencas_select_one"),
    path("subcuencas/insert/", views.subcuencas_insert, name="subcuencas_insert"),
    path("subcuencas/update/<int:id>/", views.subcuencas_update, name="subcuencas_update"),
    path("subcuencas/delete/<int:id>/", views.subcuencas_delete, name="subcuencas_delete"),
]