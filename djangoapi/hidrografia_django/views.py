# Create your views here.
#Django imports
import json
from django.http import JsonResponse
from django.views import View
from .models import Cauces, EstacionesMonitoreo, Subcuencas  

#My imports
from core.myLib.geometryTools import WkbConversor, GeometryChecks

#importar mis insert de los diferentes modelos   -- POR HACER
#CAUCES
#select all
def cauces_select_all(request):
    if request.method != "GET":
        return JsonResponse({"ok": False, "message": "Método no permitido"}, status=405)

    data = list(Cauces.objects.values())
    return JsonResponse({"ok": True, "data": data}, safe=False)

#select one
def cauces_select_one(request, id):
    if request.method != "GET":
        return JsonResponse({"ok": False, "message": "Método no permitido"}, status=405)

    try:
        cauce = Cauces.objects.values().get(id=id)
        return JsonResponse({"ok": True, "data": cauce})
    except Cauces.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Cauce no encontrado"}, status=404)
#insert
def cauces_insert(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "message": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)

        geom = None
        if body.get("geom"):
            geom = GEOSGeometry(body["geom"], srid=25830)

        cauce = Cauces.objects.create(
            nombre=body.get("nombre"),
            tipo=body.get("tipo"),
            caudal_medio=body.get("caudal_medio"),
            estado_ecologico=body.get("estado_ecologico"),
            geom=geom
        )

        return JsonResponse({
            "ok": True,
            "message": "Cauce insertado correctamente",
            "id": cauce.id
        })

    except Exception as e:
        return JsonResponse({"ok": False, "message": str(e)}, status=400)

#update
def cauces_update(request, id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "message": "Método no permitido"}, status=405)

    try:
        cauce = Cauces.objects.get(id=id)
    except Cauces.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Cauce no encontrado"}, status=404)

    try:
        body = json.loads(request.body)

        cauce.nombre = body.get("nombre", cauce.nombre)
        cauce.tipo = body.get("tipo", cauce.tipo)
        cauce.caudal_medio = body.get("caudal_medio", cauce.caudal_medio)
        cauce.estado_ecologico = body.get("estado_ecologico", cauce.estado_ecologico)

        if body.get("geom"):
            cauce.geom = GEOSGeometry(body["geom"], srid=25830)

        cauce.save()

        return JsonResponse({
            "ok": True,
            "message": "Cauce actualizado correctamente"
        })

    except Exception as e:
        return JsonResponse({"ok": False, "message": str(e)}, status=400)

#delete
def cauces_delete(request, id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "message": "Método no permitido"}, status=405)

    try:
        cauce = Cauces.objects.get(id=id)
        cauce.delete()
        return JsonResponse({"ok": True, "message": "Cauce eliminado correctamente"})
    except Cauces.DoesNotExist:
        return JsonResponse({"ok": False, "message": "Cauce no encontrado"}, status=404)
    
    
    




#ejemplos del profesor
class HelloHidrografia(View):
    def get(self, request):
        return JsonResponse({"ok":True,"message": "Hidrografia. Hello world", "data":[request.GET.dict()]})
    def post(self, request):
        return JsonResponse({"ok":True,"message": "Hidrografia. Hello world", "data":[request.POST.dict()]})

class Cauces(View):
    def post(self, request):
        d=request.POST.dict()
        r=... # Aquí iría la lógica para procesar los datos de cauces
        return JsonResponse({"ok":True,"message": "Hidrografia. Cauces", "data":[d]})