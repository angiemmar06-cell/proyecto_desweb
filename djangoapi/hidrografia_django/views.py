# Create your views here.
# Django imports
import json
from django.http import JsonResponse
from django.views import View
from .models import Cauces, EstacionesMonitoreo, Subcuencas

# My imports
from core.myLib.geometryTools import WkbConversor, GeometryChecks


# ============================================================
#                          CAUCES
# ============================================================
class CaucesView(View):
    # Tabla generada por Django: <app_label>_<modelo_lowercase>
    TABLE_NAME = 'hidrografia_django_cauces'

    def _serialize(self, cauce):
        """Convierte una instancia Cauces en un dict listo para JsonResponse."""
        return {
            'id': cauce.id,
            'nombre': cauce.nombre,
            'tipo': cauce.tipo,
            'longitud_km': cauce.longitud_km,
            'caudal_medio': cauce.caudal_medio,
            'estado_ecologico': cauce.estado_ecologico,
            'geom': cauce.geom.geojson if cauce.geom else None,
            'data_creation': cauce.data_creation.isoformat() if cauce.data_creation else None,
        }

    def get(self, request, id=None):
        # SELECT ONE
        if id:
            try:
                cauce = Cauces.objects.get(id=id)
                return JsonResponse({'ok': True, 'data': [self._serialize(cauce)]})
            except Cauces.DoesNotExist:
                return JsonResponse({'ok': False, 'message': 'Cauce no encontrado'}, status=404)
        # SELECT ALL
        cauces = Cauces.objects.all()
        return JsonResponse({'ok': True, 'data': [self._serialize(c) for c in cauces]})

    def post(self, request):
        # INSERT con comprobaciones: snap to grid + validez + no intersección
        try:
            data = json.loads(request.body)

            # 1. La geometría es obligatoria
            geom_input = data.get('geom')
            if not geom_input:
                return JsonResponse(
                    {'ok': False, 'message': 'La geometría es obligatoria'},
                    status=400
                )

            # 2. Snap to grid
            conversor = WkbConversor()
            wkb = conversor.set_wkt_from_text(geom_input)

            # 3. ¿La geometría es válida después del snap?
            gc = GeometryChecks(wkb)
            if not gc.is_geometry_valid():
                return JsonResponse(
                    {'ok': False, 'message': 'Geometría inválida tras el snap to grid', 'data': None},
                    status=400
                )

            # 4. ¿Intersecta con algún otro cauce? (ST_relate con T********)
            related = gc.check_st_relate(self.TABLE_NAME, 'T********')
            if gc.are_there_related_ids():
                return JsonResponse(
                    {'ok': False, 'message': gc.get_relate_message(), 'data': related},
                    status=400
                )

            # 5. Crear el cauce. NO pasamos:
            #    - longitud_km: se calcula automático en Cauces.save()
            #    - data_creation: la pone la BD (db_default)
            cauce = Cauces.objects.create(
                nombre=data.get('nombre'),
                tipo=data.get('tipo'),
                caudal_medio=data.get('caudal_medio'),
                estado_ecologico=data.get('estado_ecologico'),
                geom=wkb,
            )
            cauce.refresh_from_db()

            return JsonResponse({
                'ok': True,
                'message': 'Cauce insertado correctamente',
                'data': [self._serialize(cauce)]
            }, status=201)

        except Exception as e:
            return JsonResponse({'ok': False, 'message': str(e)}, status=400)

    def put(self, request, id):
        # UPDATE con las mismas 3 comprobaciones + id_to_avoid (no chocar contra sí mismo)
        try:
            cauce = Cauces.objects.get(id=id)
        except Cauces.DoesNotExist:
            return JsonResponse({'ok': False, 'message': 'Cauce no encontrado'}, status=404)

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

                # OJO: id_to_avoid=id para no detectar al propio cauce como intersección
                related = gc.check_st_relate(self.TABLE_NAME, 'T********', id_to_avoid=id)
                if gc.are_there_related_ids():
                    return JsonResponse(
                        {'ok': False, 'message': gc.get_relate_message(), 'data': related},
                        status=400
                    )
                cauce.geom = wkb

            # Actualizar campos editables solo si llegan en el body
            if 'nombre' in data:
                cauce.nombre = data['nombre']
            if 'tipo' in data:
                cauce.tipo = data['tipo']
            if 'caudal_medio' in data:
                cauce.caudal_medio = data['caudal_medio']
            if 'estado_ecologico' in data:
                cauce.estado_ecologico = data['estado_ecologico']

            cauce.save()  # recalcula longitud_km
            cauce.refresh_from_db()

            return JsonResponse({
                'ok': True,
                'message': 'Cauce actualizado correctamente',
                'data': [self._serialize(cauce)]
            })

        except Exception as e:
            return JsonResponse({'ok': False, 'message': str(e)}, status=400)

    def delete(self, request, id):
        try:
            cauce = Cauces.objects.get(id=id)
            cauce.delete()
            return JsonResponse({'ok': True, 'message': 'Cauce eliminado correctamente'}, status=200)
        except Cauces.DoesNotExist:
            return JsonResponse({'ok': False, 'message': 'Cauce no encontrado'}, status=404)


# ============================================================
#                  ESTACIONES DE MONITOREO
# ============================================================
class EstacionesMonitoreoView(View):
    TABLE_NAME = 'hidrografia_django_estacionesmonitoreo'

    def _serialize(self, estacion):
        return {
            'id': estacion.id,
            'nombre': estacion.nombre,
            'tipo': estacion.tipo,
            'organismo': estacion.organismo,
            'estado': estacion.estado,
            'fecha_instalacion': estacion.fecha_instalacion.isoformat() if estacion.fecha_instalacion else None,
            'geom': estacion.geom.geojson if estacion.geom else None,
            'data_creation': estacion.data_creation.isoformat() if estacion.data_creation else None,
        }

    def get(self, request, id=None):
        if id:
            try:
                estacion = EstacionesMonitoreo.objects.get(id=id)
                return JsonResponse({'ok': True, 'data': [self._serialize(estacion)]})
            except EstacionesMonitoreo.DoesNotExist:
                return JsonResponse({'ok': False, 'message': 'Estación de Monitoreo no encontrada'}, status=404)
        estaciones = EstacionesMonitoreo.objects.all()
        return JsonResponse({'ok': True, 'data': [self._serialize(e) for e in estaciones]})

    def post(self, request):
        try:
            data = json.loads(request.body)

            geom_input = data.get('geom')
            if not geom_input:
                return JsonResponse({'ok': False, 'message': 'La geometría es obligatoria'}, status=400)

            conversor = WkbConversor()
            wkb = conversor.set_wkt_from_text(geom_input)

            gc = GeometryChecks(wkb)
            if not gc.is_geometry_valid():
                return JsonResponse(
                    {'ok': False, 'message': 'Geometría inválida tras el snap to grid', 'data': None},
                    status=400
                )

            related = gc.check_st_relate(self.TABLE_NAME, 'T********')
            if gc.are_there_related_ids():
                return JsonResponse(
                    {'ok': False, 'message': gc.get_relate_message(), 'data': related},
                    status=400
                )

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

    def put(self, request, id):
        try:
            estacion = EstacionesMonitoreo.objects.get(id=id)
        except EstacionesMonitoreo.DoesNotExist:
            return JsonResponse({'ok': False, 'message': 'Estación de Monitoreo no encontrada'}, status=404)

        try:
            data = json.loads(request.body)

            if data.get('geom'):
                conversor = WkbConversor()
                wkb = conversor.set_wkt_from_text(data['geom'])

                gc = GeometryChecks(wkb)
                if not gc.is_geometry_valid():
                    return JsonResponse(
                        {'ok': False, 'message': 'Geometría inválida tras el snap to grid', 'data': None},
                        status=400
                    )

                related = gc.check_st_relate(self.TABLE_NAME, 'T********', id_to_avoid=id)
                if gc.are_there_related_ids():
                    return JsonResponse(
                        {'ok': False, 'message': gc.get_relate_message(), 'data': related},
                        status=400
                    )
                estacion.geom = wkb

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

    def delete(self, request, id):
        try:
            estacion = EstacionesMonitoreo.objects.get(id=id)
            estacion.delete()
            return JsonResponse({'ok': True, 'message': 'Estación de Monitoreo eliminada correctamente'}, status=200)
        except EstacionesMonitoreo.DoesNotExist:
            return JsonResponse({'ok': False, 'message': 'Estación de Monitoreo no encontrada'}, status=404)


# ============================================================
#                        SUBCUENCAS
# ============================================================
class SubcuencasView(View):
    TABLE_NAME = 'hidrografia_django_subcuencas'

    def _serialize(self, subcuenca):
        return {
            'id': subcuenca.id,
            'nombre': subcuenca.nombre,
            'codigo': subcuenca.codigo,
            'area_km2': subcuenca.area_km2,
            'perimetro_km': subcuenca.perimetro_km,
            'uso_suelo': subcuenca.uso_suelo,
            'geom': subcuenca.geom.geojson if subcuenca.geom else None,
            'data_creation': subcuenca.data_creation.isoformat() if subcuenca.data_creation else None,
        }

    def get(self, request, id=None):
        if id:
            try:
                subcuenca = Subcuencas.objects.get(id=id)
                return JsonResponse({'ok': True, 'data': [self._serialize(subcuenca)]})
            except Subcuencas.DoesNotExist:
                return JsonResponse({'ok': False, 'message': 'Subcuenca no encontrada'}, status=404)
        subcuencas = Subcuencas.objects.all()
        return JsonResponse({'ok': True, 'data': [self._serialize(s) for s in subcuencas]})

    def post(self, request):
        try:
            data = json.loads(request.body)

            geom_input = data.get('geom')
            if not geom_input:
                return JsonResponse({'ok': False, 'message': 'La geometría es obligatoria'}, status=400)

            conversor = WkbConversor()
            wkb = conversor.set_wkt_from_text(geom_input)

            gc = GeometryChecks(wkb)
            if not gc.is_geometry_valid():
                return JsonResponse(
                    {'ok': False, 'message': 'Geometría inválida tras el snap to grid', 'data': None},
                    status=400
                )

            related = gc.check_st_relate(self.TABLE_NAME, 'T********')
            if gc.are_there_related_ids():
                return JsonResponse(
                    {'ok': False, 'message': gc.get_relate_message(), 'data': related},
                    status=400
                )

            # NO pasamos area_km2 ni perimetro_km: el modelo los calcula en save()
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

    def put(self, request, id):
        try:
            subcuenca = Subcuencas.objects.get(id=id)
        except Subcuencas.DoesNotExist:
            return JsonResponse({'ok': False, 'message': 'Subcuenca no encontrada'}, status=404)

        try:
            data = json.loads(request.body)

            if data.get('geom'):
                conversor = WkbConversor()
                wkb = conversor.set_wkt_from_text(data['geom'])

                gc = GeometryChecks(wkb)
                if not gc.is_geometry_valid():
                    return JsonResponse(
                        {'ok': False, 'message': 'Geometría inválida tras el snap to grid', 'data': None},
                        status=400
                    )

                related = gc.check_st_relate(self.TABLE_NAME, 'T********', id_to_avoid=id)
                if gc.are_there_related_ids():
                    return JsonResponse(
                        {'ok': False, 'message': gc.get_relate_message(), 'data': related},
                        status=400
                    )
                subcuenca.geom = wkb

            if 'nombre' in data:
                subcuenca.nombre = data['nombre']
            if 'codigo' in data:
                subcuenca.codigo = data['codigo']
            if 'uso_suelo' in data:
                subcuenca.uso_suelo = data['uso_suelo']

            subcuenca.save()  # recalcula area_km2 y perimetro_km
            subcuenca.refresh_from_db()

            return JsonResponse({
                'ok': True,
                'message': 'Subcuenca actualizada correctamente',
                'data': [self._serialize(subcuenca)]
            })

        except Exception as e:
            return JsonResponse({'ok': False, 'message': str(e)}, status=400)

    def delete(self, request, id):
        try:
            subcuenca = Subcuencas.objects.get(id=id)
            subcuenca.delete()
            return JsonResponse({'ok': True, 'message': 'Subcuenca eliminada correctamente'}, status=200)
        except Subcuencas.DoesNotExist:
            return JsonResponse({'ok': False, 'message': 'Subcuenca no encontrada'}, status=404)
