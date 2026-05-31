from django.contrib import admin
from .models import Cauces, EstacionesMonitoreo, Subcuencas

# Register your models here.
admin.site.register(Cauces)
admin.site.register(EstacionesMonitoreo)
admin.site.register(Subcuencas)
