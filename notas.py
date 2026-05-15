#importar mis insert de los diferentes modelos   -- POR HACER
class CaucesView(View):
    def get(self, request, id=None):
        if id:
            return cauces_select_one(request, id)
        else:
            return cauces_select_all(request)

    def post(self, request, id=None):
        if id:
            return cauces_update(request, id)
        else:
            return cauces_insert(request)

    def delete(self, request, id):
        return cauces_delete(request, id)
    
#CAUCES
#select all
def cauces_select_all(request): 
    if request.method != "GET": #verifico el metodo HTTP. Solo permito GET para este endpoint
        return JsonResponse({"ok": False, "message": "Método no permitido"}, status=405)
    data = list(Cauces.objects.values()) #obtengo todos los registros de la tabla Cauces y los convierto a una lista de diccionarios
    return JsonResponse({"ok": True, "data": data}, safe=False) #devuelvo la respuesta en formato JSON. El parámetro safe=False permite devolver una lista en lugar de un diccionario, que es el formato esperado por JsonResponse.

#select one
def cauces_select_one(request, id):
    if request.method != "GET": #verifico el metodo HTTP. Solo permito GET para este endpoint
        return JsonResponse({"ok": False, "message": "Método no permitido"}, status=405)
    try:
        cauce = Cauces.objects.values().get(id=id) #obtengo el registro de la tabla Cauces con el id especificado y lo convierto a un diccionario
        return JsonResponse({"ok": True, "data": cauce})
    except Cauces.DoesNotExist:#si no existe el registro con el id especificado, devuelvo un error 404
        return JsonResponse({"ok": False, "message": "Cauce no encontrado"}, status=404)
#insert
def cauces_insert(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "message": "Método no permitido"}, status=405)
    try:
        body = json.loads(request.body) #leo el cuerpo de la solicitud y lo convierto de JSON a un diccionario de Python
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
    
