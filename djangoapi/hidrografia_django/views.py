# Create your views here.
#Django imports
import json
from django.http import JsonResponse
from django.views import View
from .models import Cauces, EstacionesMonitoreo, Subcuencas  

#My imports
from core.myLib.geometryTools import WkbConversor, GeometryChecks

#importar mis insert de los diferentes modelos   -- POR HACER
class CaucesView(View):
    def get (self, request, id=None):
        if id:
            try:
                cauce = Cauces.objects.get(id=id) # Obtener el cauce por su ID
                data = {
                    'id': cauce.id,
                    'nombre': cauce.nombre,
                    'longitud_km': cauce.longitud_km,
                    'estado_ecologico': cauce.estado_ecologico,
                    'geom': WkbConversor.to_geojson(cauce.geom),
                    'data_creation': cauce.data_creation.isoformat() if cauce.data_creation else None 
                    #isoformat() convierte el datetime a un formato legible para JSON, y se maneja el caso de que data_creation sea None
                }
                return JsonResponse(data)
            except Cauces.DoesNotExist:
                return JsonResponse({'error': 'Cauce no encontrado'}, status=404)
        else:
            cauces = Cauces.objects.all()
            data = []
            for cauce in cauces:
                data.append({
                    'id': cauce.id,
                    'nombre': cauce.nombre,
                    'longitud_km': cauce.longitud_km,
                    'estado_ecologico': cauce.estado_ecologico,
                    'geom': WkbConversor.to_geojson(cauce.geom),
                    'data_creation': cauce.data_creation.isoformat() if cauce.data_creation else None
                })
            return JsonResponse(data, safe=False)
        
    def post(self, request):
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')
            geom = data.get('geom')

            if not nombre or not geom:
                return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)

            if not GeometryChecks.is_valid_geometry(geom):
                return JsonResponse({'error': 'Geometría no válida'}, status=400)

            cauce = Cauces.objects.create(nombre=nombre, geom=WkbConversor.from_geojson(geom))
            return JsonResponse({'id': cauce.id, 'nombre': cauce.nombre}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON no válido'}, status=400)
    def delete(self, request, id):
        try:
            cauce = Cauces.objects.get(id=id)
            cauce.delete()
            return JsonResponse({'message': 'Cauce eliminado correctamente'}, status=200)
        except Cauces.DoesNotExist:
            return JsonResponse({'error': 'Cauce no encontrado'}, status=404)
class EstacionesMonitoreoView(View):
    def get (self, request, id=None):
        if id:
            try:
                estacion = EstacionesMonitoreo.objects.get(id=id)
                data = {
                    'id': estacion.id,
                    'nombre': estacion.nombre,
                    'geom': WkbConversor.to_geojson(estacion.geom)
                }
                return JsonResponse(data)
            except EstacionesMonitoreo.DoesNotExist:
                return JsonResponse({'error': 'Estación de Monitoreo no encontrada'}, status=404)
        else:
            estaciones = EstacionesMonitoreo.objects.all()
            data = []
            for estacion in estaciones:
                data.append({
                    'id': estacion.id,
                    'nombre': estacion.nombre,
                    'geom': WkbConversor.to_geojson(estacion.geom)
                })
            return JsonResponse(data, safe=False)