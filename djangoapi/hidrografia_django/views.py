# Create your views here.
#Django imports
from django.http import JsonResponse
from django.views import View

#My imports
from core.myLib.geometryTools import WkbConversor, GeometryChecks

#importar mis insert de los diferentes modelos   -- POR HACER

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