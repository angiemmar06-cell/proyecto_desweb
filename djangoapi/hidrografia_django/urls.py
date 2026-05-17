from django.urls import path
from . import views

#lo realizo con el metodo HTTP verbos, por lo que cada URL se corresponde con una acción concreta (GET, POST, PUT, DELETE)
urlpatterns = [
    #uso as.view() para convertir la clase en una vista que pueda ser llamada por la URL
     # Cauces
    path("cauces/", views.CaucesView.as_view(), name="cauces"),
    path("cauces/<int:id>/", views.CaucesView.as_view(), name="cauces_view"),

    # Estaciones de Monitoreo:
    path("estaciones_monitoreo/", views.EstacionesMonitoreoView.as_view(), name="estaciones_monitoreo"),
    path("estaciones_monitoreo/<int:id>/", views.EstacionesMonitoreoView.as_view(), name="estaciones_monitoreo_view"),

    # Subcuencas:
    path("subcuencas/", views.SubcuencasView.as_view(), name="subcuencas"),
    path("subcuencas/<int:id>/", views.SubcuencasView.as_view(), name="subcuencas_view"),

]