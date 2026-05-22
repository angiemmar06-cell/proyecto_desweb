# Vistas (views) de la app hidrografia_django.
# Cada vista representa una tabla y soporta las operaciones GET, POST, PUT y DELETE.

# json: para leer el cuerpo de la petición que viene en formato JSON
import json
# JsonResponse: para devolver respuestas en formato JSON al frontend
from django.http import JsonResponse
# View: clase base de Django para crear vistas por clases (CBV)
from django.views import View
# Modelos de nuestras tres tablas
from .models import Cauces, EstacionesMonitoreo, Subcuencas

# Estas dos importaciones permiten desactivar la protección CSRF en las vistas, las CSRF es una medida de seguridad que Django 
# aplica por defecto para evitar ataques de tipo Cross-Site Request Forgery en formularios HTML.
# Lo hacemos porque estamos haciendo una API REST y la consume Angular (no un formulario HTML clásico).
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Herramientas para trabajar con geometrías (las creó el profesor en core/myLib/geometryTools.py):
#   - WkbConversor: aplica snap to grid y convierte texto WKT en formato binario WKB
#   - GeometryChecks: comprueba si la geometría es válida y si se solapa con otras existentes
from core.myLib.geometryTools import WkbConversor, GeometryChecks


# Vista que maneja la tabla de cauces (líneas).
# El decorador csrf_exempt permite que Angular pueda hacer POST/PUT/DELETE sin enviar token CSRF.
@method_decorator(csrf_exempt, name='dispatch')
class CaucesView(View):
    # Nombre real de la tabla en PostgreSQL. Lo usamos para las comprobaciones de geometría.
    TABLE_NAME = 'hidrografia_django_cauces'

    # Convierte un objeto Cauces de la base de datos a un diccionario Python.
    # Ese diccionario se devuelve al frontend dentro del JSON.
    def _serialize(self, cauce):
        return {
            'id': cauce.id,
            'nombre': cauce.nombre,
            'tipo': cauce.tipo,
            'longitud_km': cauce.longitud_km,
            'caudal_medio': cauce.caudal_medio,
            'estado_ecologico': cauce.estado_ecologico,
            # La geometría se devuelve en formato WKT (texto plano legible), igual al que el usuario escribe
            'geom': cauce.geom.wkt if cauce.geom else None,
            'data_creation': cauce.data_creation.isoformat() if cauce.data_creation else None,
        }

    # Método GET: si llega un id devuelve un cauce, si no llega devuelve todos.
    def get(self, request, id=None):
        # Caso "selectone": el frontend pidió un cauce concreto por su id
        if id:
            try:
                cauce = Cauces.objects.get(id=id) 
                return JsonResponse({'ok': True, 'message': 'Cauce recuperado', 'data': [self._serialize(cauce)]})
            except Cauces.DoesNotExist:
                # Si no existe el id devolvemos 404 con mensaje claro
                return JsonResponse({'ok': False, 'message': 'Cauce no encontrado'}, status=404)
        # Caso "selectall": devolvemos todos los cauces
        cauces = Cauces.objects.all()
        return JsonResponse({'ok': True, 'message': 'Cauces recuperados', 'data': [self._serialize(c) for c in cauces]})

    # Método POST: crea un cauce nuevo aplicando tres comprobaciones de geometría.
    def post(self, request):
        try:
            # Leemos el JSON que envió el frontend
            data = json.loads(request.body) #el body de la petición es un texto JSON, lo convertimos a diccionario Python con json.loads() para poder trabajar con él. 
            # Comprobación 1: la geometría es obligatoria
            geom_input = data.get('geom')
            if not geom_input:
                return JsonResponse(
                    {'ok': False, 'message': 'La geometría es obligatoria'},
                    status=400
                )

            # Comprobación 2: ajustamos la geometría a una rejilla de precisión (snap to grid)
            # WkbConversor ejecuta por dentro un ST_SNAPTOGRID en PostgreSQL
            conversor = WkbConversor()
            wkb = conversor.set_wkt_from_text(geom_input) #con el set_wkt_from_text() hacemos el snap to grid y 
            #convertimos el texto WKT en formato binario WKB, que es el que entiende PostGIS para almacenar la geometría. 
            # El snap to grid es importante para evitar problemas de precisión que pueden hacer que una geometría que parece 
            # correcta no lo sea realmente a nivel computacional, lo que puede causar errores en las comprobaciones de validez 
            # o solape. Al aplicar snap to grid, nos aseguramos de que las coordenadas se ajusten a una rejilla definida por la 
            # precisión, lo que mejora la robustez de las operaciones geométricas.

            # Comprobación 3: la geometría debe ser válida (ST_IsValid)
            gc = GeometryChecks(wkb)
            if not gc.is_geometry_valid():
                return JsonResponse(
                    {'ok': False, 'message': 'Geometría inválida tras el snap to grid', 'data': None},
                    status=400
                )

            # Comprobación 4: la geometría no debe solaparse con otros cauces ya existentes
            # ST_relate con matriz 'T********' detecta intersecciones de interior
            related = gc.check_st_relate(self.TABLE_NAME, 'T********')
            if gc.are_there_related_ids():
                # Mensaje claro para el usuario en lugar del texto técnico de ST_relate
                return JsonResponse(
                    {'ok': False, 'message': 'El cauce se cruza con otros cauces ya existentes', 'data': related},
                    status=400
                )

            # Si pasó todas las comprobaciones, creamos el cauce.
            # NO paso longitud_km ni data_creation porque se rellenan solos:
            # longitud_km lo calcula el método save() del modelo Cauces
            # data_creation la pone la base de datos por db_default
            cauce = Cauces.objects.create(
                nombre=data.get('nombre'),
                tipo=data.get('tipo'),
                caudal_medio=data.get('caudal_medio'), #trae estos datos del body del JSON que envió el frontend.
                estado_ecologico=data.get('estado_ecologico'),
                geom=wkb,
            )
            # refresh_from_db trae los valores calculados (longitud_km y data_creation)
            cauce.refresh_from_db()

            return JsonResponse({
                'ok': True,
                'message': 'Cauce insertado correctamente',
                'data': [self._serialize(cauce)]
            }, status=201)

        except Exception as e:
            # Si algo falla devolvemos el error con el mensaje de la excepción
            return JsonResponse({'ok': False, 'message': str(e)}, status=400)

    # Método PUT: actualiza un cauce existente.
    # Repite las comprobaciones de geometría pero excluye al propio cauce de la verificación de solape.
    def put(self, request, id):
        # Primero comprobamos que el cauce a actualizar existe
        try:
            cauce = Cauces.objects.get(id=id)
        except Cauces.DoesNotExist:
            return JsonResponse({'ok': False, 'message': 'Cauce no encontrado'}, status=404)

        try:
            data = json.loads(request.body)

            # Si el frontend mandó nueva geometría, la validamos como en el insert
            if data.get('geom'):
                conversor = WkbConversor()
                wkb = conversor.set_wkt_from_text(data['geom'])

                gc = GeometryChecks(wkb)
                if not gc.is_geometry_valid():
                    return JsonResponse(
                        {'ok': False, 'message': 'Geometría inválida tras el snap to grid', 'data': None},
                        status=400
                    )

                # id_to_avoid=id evita que el cauce salga como "intersección consigo mismo"
                related = gc.check_st_relate(self.TABLE_NAME, 'T********', id_to_avoid=id)
                if gc.are_there_related_ids():
                    return JsonResponse(
                        {'ok': False, 'message': 'El cauce se cruza con otros cauces ya existentes', 'data': related},
                        status=400
                    )
                cauce.geom = wkb

            # Solo actualizamos los campos que llegan en el body.
            # Si el cliente no manda un campo, mantenemos el valor actual.
            if 'nombre' in data:
                cauce.nombre = data['nombre']
            if 'tipo' in data:
                cauce.tipo = data['tipo']
            if 'caudal_medio' in data:
                cauce.caudal_medio = data['caudal_medio']
            if 'estado_ecologico' in data:
                cauce.estado_ecologico = data['estado_ecologico']

            # save() recalcula longitud_km automáticamente
            cauce.save()
            cauce.refresh_from_db()

            return JsonResponse({
                'ok': True,
                'message': 'Cauce actualizado correctamente',
                'data': [self._serialize(cauce)]
            })

        except Exception as e:
            return JsonResponse({'ok': False, 'message': str(e)}, status=400)

    # Método DELETE: borra un cauce por su id.
    def delete(self, request, id):
        try:
            cauce = Cauces.objects.get(id=id)
            cauce.delete()
            return JsonResponse({'ok': True, 'message': 'Cauce eliminado correctamente'}, status=200)
        except Cauces.DoesNotExist:
            return JsonResponse({'ok': False, 'message': 'Cauce no encontrado'}, status=404)


# Vista que maneja la tabla de estaciones de monitoreo (puntos).
# csrf_exempt por el mismo motivo: peticiones desde Angular sin token CSRF.
@method_decorator(csrf_exempt, name='dispatch')
class EstacionesMonitoreoView(View):
    # Nombre real de la tabla en PostgreSQL
    TABLE_NAME = 'hidrografia_django_estacionesmonitoreo'

    # Convierte una estación a diccionario para devolverla como JSON
    def _serialize(self, estacion):
        return {
            'id': estacion.id,
            'nombre': estacion.nombre,
            'tipo': estacion.tipo,
            'organismo': estacion.organismo,
            'estado': estacion.estado,
            'fecha_instalacion': estacion.fecha_instalacion.isoformat() if estacion.fecha_instalacion else None,
            # Geometría en formato WKT (texto plano)
            'geom': estacion.geom.wkt if estacion.geom else None,
            'data_creation': estacion.data_creation.isoformat() if estacion.data_creation else None,
        }

    # Método GET: selectone si llega id, selectall si no llega
    def get(self, request, id=None):
        if id:
            try:
                estacion = EstacionesMonitoreo.objects.get(id=id)
                return JsonResponse({'ok': True, 'message': 'Estación de Monitoreo recuperada', 'data': [self._serialize(estacion)]})
            except EstacionesMonitoreo.DoesNotExist:
                return JsonResponse({'ok': False, 'message': 'Estación de Monitoreo no encontrada'}, status=404)
        estaciones = EstacionesMonitoreo.objects.all()
        return JsonResponse({'ok': True, 'message': 'Estaciones de Monitoreo recuperadas', 'data': [self._serialize(e) for e in estaciones]})

    # Método POST: crea una estación nueva con las mismas comprobaciones que cauces
    def post(self, request):
        try:
            data = json.loads(request.body)

            # La geometría es obligatoria
            geom_input = data.get('geom')
            if not geom_input:
                return JsonResponse({'ok': False, 'message': 'La geometría es obligatoria'}, status=400)

            # Snap to grid
            conversor = WkbConversor()
            wkb = conversor.set_wkt_from_text(geom_input)

            # Validez de la geometría
            gc = GeometryChecks(wkb)
            if not gc.is_geometry_valid():
                return JsonResponse(
                    {'ok': False, 'message': 'Geometría inválida tras el snap to grid', 'data': None},
                    status=400
                )

            # No debe haber otra estación en la misma ubicación
            related = gc.check_st_relate(self.TABLE_NAME, 'T********')
            if gc.are_there_related_ids():
                return JsonResponse(
                    {'ok': False, 'message': 'Ya existe una estación de monitoreo en esa ubicación', 'data': related},
                    status=400
                )

            # Crear la estación. data_creation la pone la base de datos por db_default
            estacion = EstacionesMonitoreo.objects.create(
                nombre=data.get('nombre'),
                tipo=data.get('tipo'),
                organismo=data.get('organismo'),
                estado=data.get('estado'),
                fecha_instalacion=data.get('fecha_instalacion'),
                geom=wkb,
            )
            estacion.refresh_from_db()

            return JsonResponse({
                'ok': True,
                'message': 'Estación de Monitoreo insertada correctamente',
                'data': [self._serialize(estacion)]
            }, status=201)

        except Exception as e:
            return JsonResponse({'ok': False, 'message': str(e)}, status=400)

    # Método PUT: actualiza una estación existente
    def put(self, request, id):
        try:
            estacion = EstacionesMonitoreo.objects.get(id=id)
        except EstacionesMonitoreo.DoesNotExist:
            return JsonResponse({'ok': False, 'message': 'Estación de Monitoreo no encontrada'}, status=404)

        try:
            data = json.loads(request.body)

            # Si llega nueva geometría, validarla
            if data.get('geom'):
                conversor = WkbConversor()
                wkb = conversor.set_wkt_from_text(data['geom'])

                gc = GeometryChecks(wkb)
                if not gc.is_geometry_valid():
                    return JsonResponse(
                        {'ok': False, 'message': 'Geometría inválida tras el snap to grid', 'data': None},
                        status=400
                    )

                # id_to_avoid evita auto-detección como solape
                related = gc.check_st_relate(self.TABLE_NAME, 'T********', id_to_avoid=id)
                if gc.are_there_related_ids():
                    return JsonResponse(
                        {'ok': False, 'message': 'Ya existe una estación de monitoreo en esa ubicación', 'data': related},
                        status=400
                    )
                estacion.geom = wkb

            # Actualizamos solo los campos que llegan
            if 'nombre' in data:
                estacion.nombre = data['nombre']
            if 'tipo' in data:
                estacion.tipo = data['tipo']
            if 'organismo' in data:
                estacion.organismo = data['organismo']
            if 'estado' in data:
                estacion.estado = data['estado']
            if 'fecha_instalacion' in data:
                estacion.fecha_instalacion = data['fecha_instalacion']

            estacion.save()
            estacion.refresh_from_db()

            return JsonResponse({
                'ok': True,
                'message': 'Estación de Monitoreo actualizada correctamente',
                'data': [self._serialize(estacion)]
            })

        except Exception as e:
            return JsonResponse({'ok': False, 'message': str(e)}, status=400)

    # Método DELETE: borra una estación por id
    def delete(self, request, id):
        try:
            estacion = EstacionesMonitoreo.objects.get(id=id)
            estacion.delete()
            return JsonResponse({'ok': True, 'message': 'Estación de Monitoreo eliminada correctamente'}, status=200)
        except EstacionesMonitoreo.DoesNotExist:
            return JsonResponse({'ok': False, 'message': 'Estación de Monitoreo no encontrada'}, status=404)


# Vista que maneja la tabla de subcuencas (polígonos).
# csrf_exempt por el mismo motivo: peticiones desde Angular sin token CSRF.
@method_decorator(csrf_exempt, name='dispatch')
class SubcuencasView(View):
    # Nombre real de la tabla en PostgreSQL
    TABLE_NAME = 'hidrografia_django_subcuencas'

    # Convierte una subcuenca a diccionario para devolverla como JSON
    def _serialize(self, subcuenca):
        return {
            'id': subcuenca.id,
            'nombre': subcuenca.nombre,
            'codigo': subcuenca.codigo,
            'area_km2': subcuenca.area_km2,
            'perimetro_km': subcuenca.perimetro_km,
            'uso_suelo': subcuenca.uso_suelo,
            # Geometría en formato WKT (texto plano)
            'geom': subcuenca.geom.wkt if subcuenca.geom else None,
            'data_creation': subcuenca.data_creation.isoformat() if subcuenca.data_creation else None,
        }

    # Método GET: selectone si llega id, selectall si no llega
    def get(self, request, id=None):
        if id:
            try:
                subcuenca = Subcuencas.objects.get(id=id)
                return JsonResponse({'ok': True, 'message': 'Subcuenca recuperada', 'data': [self._serialize(subcuenca)]})
            except Subcuencas.DoesNotExist:
                return JsonResponse({'ok': False, 'message': 'Subcuenca no encontrada'}, status=404)
        subcuencas = Subcuencas.objects.all()
        return JsonResponse({'ok': True, 'message': 'Subcuencas recuperadas', 'data': [self._serialize(s) for s in subcuencas]})

    # Método POST: crea una subcuenca nueva con las mismas comprobaciones que cauces
    def post(self, request):
        try:
            data = json.loads(request.body)

            # La geometría es obligatoria
            geom_input = data.get('geom')
            if not geom_input:
                return JsonResponse({'ok': False, 'message': 'La geometría es obligatoria'}, status=400)

            # Snap to grid
            conversor = WkbConversor()
            wkb = conversor.set_wkt_from_text(geom_input)

            # Validez de la geometría
            gc = GeometryChecks(wkb)
            if not gc.is_geometry_valid():
                return JsonResponse(
                    {'ok': False, 'message': 'Geometría inválida tras el snap to grid', 'data': None},
                    status=400
                )

            # No debe solaparse con otras subcuencas
            related = gc.check_st_relate(self.TABLE_NAME, 'T********')
            if gc.are_there_related_ids():
                return JsonResponse(
                    {'ok': False, 'message': 'La subcuenca se solapa con otras subcuencas existentes', 'data': related},
                    status=400
                )

            # Crear la subcuenca. area_km2 y perimetro_km se calculan en el save() del modelo.
            subcuenca = Subcuencas.objects.create(
                nombre=data.get('nombre'),
                codigo=data.get('codigo'),
                uso_suelo=data.get('uso_suelo'),
                geom=wkb,
            )
            subcuenca.refresh_from_db()

            return JsonResponse({
                'ok': True,
                'message': 'Subcuenca insertada correctamente',
                'data': [self._serialize(subcuenca)]
            }, status=201)

        except Exception as e:
            return JsonResponse({'ok': False, 'message': str(e)}, status=400)

    # Método PUT: actualiza una subcuenca existente
    def put(self, request, id):
        try:
            subcuenca = Subcuencas.objects.get(id=id)
        except Subcuencas.DoesNotExist:
            return JsonResponse({'ok': False, 'message': 'Subcuenca no encontrada'}, status=404)

        try:
            data = json.loads(request.body)

            # Si llega nueva geometría, validarla
            if data.get('geom'):
                conversor = WkbConversor()
                wkb = conversor.set_wkt_from_text(data['geom'])

                gc = GeometryChecks(wkb)
                if not gc.is_geometry_valid():
                    return JsonResponse(
                        {'ok': False, 'message': 'Geometría inválida tras el snap to grid', 'data': None},
                        status=400
                    )

                # id_to_avoid evita auto-detección como solape
                related = gc.check_st_relate(self.TABLE_NAME, 'T********', id_to_avoid=id)
                if gc.are_there_related_ids():
                    return JsonResponse(
                        {'ok': False, 'message': 'La subcuenca se solapa con otras subcuencas existentes', 'data': related},
                        status=400
                    )
                subcuenca.geom = wkb

            # Actualizamos solo los campos que llegan
            if 'nombre' in data:
                subcuenca.nombre = data['nombre']
            if 'codigo' in data:
                subcuenca.codigo = data['codigo']
            if 'uso_suelo' in data:
                subcuenca.uso_suelo = data['uso_suelo']

            # save() recalcula area_km2 y perimetro_km
            subcuenca.save()
            subcuenca.refresh_from_db()

            return JsonResponse({
                'ok': True,
                'message': 'Subcuenca actualizada correctamente',
                'data': [self._serialize(subcuenca)]
            })

        except Exception as e:
            return JsonResponse({'ok': False, 'message': str(e)}, status=400)

    # Método DELETE: borra una subcuenca por id
    def delete(self, request, id):
        try:
            subcuenca = Subcuencas.objects.get(id=id)
            subcuenca.delete()
            return JsonResponse({'ok': True, 'message': 'Subcuenca eliminada correctamente'}, status=200)
        except Subcuencas.DoesNotExist:
            return JsonResponse({'ok': False, 'message': 'Subcuenca no encontrada'}, status=404)
