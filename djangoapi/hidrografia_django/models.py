from django.db import models
#Para usar los campos de geometría
from django.contrib.gis.db import models as gis_models
#Para zona horaria
import django.utils.timezone as djangoTimezone

# Create your models here. --> el nombre de la clases empieza en mayuscula    
# class Cauces(models.Model):
#     nombre = models.TextField(blank=True, null=True)
#     tipo = models.CharField(max_length= 20, blank=True, null=True)
#     longitud_km = models.FloatField(blank=True, null=True)
#     caudal_medio = models.FloatField(blank=True, null=True)
#     estado_ecologico = models.CharField(max_length=100, blank=True, null=True)
#     geom = gis_models.LineStringField(srid=25830,blank=True, null=True) 
#     data_creation = models.DateTimeField(blank = True, db_default=djangoTimezone.now())
    
#     def save(self, *args, **kwargs):
#         if self.geom:
#             self.longitud_km = self.geom.length
#         super().save(*args, **kwargs)
        
# class EstacionesMonitoreo(models.Model):
#     nombre = models.TextField(blank=True, null=True)
#     tipo = models.CharField(max_length= 20, blank=True, null=True)
#     organismo = models.CharField(max_length= 50, blank=True, null=True)
#     estado = models.CharField(max_length= 100, blank=True, null=True)
#     fecha_instalacion = models.DateField(blank=True, null=True)
#     geom = gis_models.PointField(srid=25830,blank=True, null=True) 
#     data_creation = models.DateTimeField(blank = True, db_default=djangoTimezone.now())

# class Subcuencas(models.Model):
#     nombre = models.TextField(blank=True, null=True)
#     codigo = models.CharField(max_length= 10, blank=True, null=True)
#     area_km2 = models.FloatField(blank=True, null=True)
#     perimetro_km = models.FloatField(blank=True, null=True)
#     uso_suelo = models.CharField(max_length=20, blank=True, null=True)
#     geom = gis_models.PolygonField(srid=25830,blank=True, null=True) 
#     data_creation = models.DateTimeField(blank = True, db_default=djangoTimezone.now())

    def save(self, *args, **kwargs):
            # Calculate values from the geometry before saving
            if self.geom:
                self.area_km2 = self.geom.area
                self.perimetro_km = self.geom.length
            
            super().save(*args, **kwargs)