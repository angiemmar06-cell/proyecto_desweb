from django.contrib.gis.geos import GEOSGeometry
from django.forms.models import model_to_dict
from django.db import connection

from hidrografia_django.models import EstacionesMonitoreo as EstacionesMonitoreoModel
from djangoapi.settings import EPSG_FOR_GEOMETRIES, ST_SNAP_PRECISION


class EstacionesMonitoreo:
    
    def insert(self, d:dict):
        #we first get the snapped wkb format for the geometry:
        cur=connection.cursor()
        query="select st_snaptogrid(st_geomfromtext(%s, %s),%s)"
        cur.execute(query, [d['geom'],EPSG_FOR_GEOMETRIES, ST_SNAP_PRECISION])
        snapped_wkb_geometry=cur.fetchall()[0][0]
        
        print(f'snapped_wkb_geometry: {snapped_wkb_geometry}')

        #now we can check if it is valid as before:
        g=GEOSGeometry(snapped_wkb_geometry, srid=EPSG_FOR_GEOMETRIES)
        if g.valid:
            print("Geometría válida")
        else:
            return {'ok': False, 'message':'Invalid geometry', 'data': None}

        #Now we can check if it intersects with another geomtry in the same layer
        #check if the geometry intersects any existing building
        query = """ 
            select id from hidrografia_django_subcuencas where st_within(
                %s,
                geom
            )
        """
        cur.execute(query, [snapped_wkb_geometry])
        r = cur.fetchall()

        if len(r) == 0:
            return {'ok': False, 'message': 'El punto no está dentro de ninguna subcuenca', 'data': None}
        
        d['geom']=g
        b=EstacionesMonitoreoModel(**d)
        b.save()
        d=model_to_dict(b)
        d['geom']=g.wkt
        d['data_creation']=d['data_creation'].strftime("%Y-%m-%d %H:%M:%S")
        return {'ok': True, 'message':'Estacion de Monitoreo inserted', 'data': [d]}
    
    def selectone(self, d:dict):
        # Busca UNA subcuenca por id usando el modelo Django
        # Django traduce esto a: SELECT * FROM hidrografia_django_subcuencas WHERE id = X
        f = EstacionesMonitoreoModel.objects.filter(id=d['id'])
        
        # filter() devuelve un QuerySet (como una lista perezosa)
        # list() lo convierte en una lista real de objetos Python
        l = list(f)
        
        # Si no encontró nada, devolvemos error
        if len(l) == 0:
            return {'ok': False, 'message': f"No existe una estacion de monitoreo con id {d['id']}", 'data': None}
        
        # Tomamos el primer (y único) resultado
        b = l[0]
        
        # model_to_dict convierte el objeto Django a un diccionario
        # Es como pasar de b.nombre, b.codigo, b.area_km2...
        # a {'nombre': '...', 'codigo': '...', 'area_km2': ...}
        d = model_to_dict(b)
        
        # La geometría viene como objeto, la convertimos a texto legible (WKT)
        d['geom'] = b.geom.wkt
        
        # La fecha viene como objeto datetime, la convertimos a texto
        d['data_creation'] = d['data_creation'].strftime("%Y-%m-%d %H:%M:%S")
        
        return {'ok': True, 'message': 'Estacion de monitoreo encontrada', 'data': [d]}


    def selectall(self):
        # Trae TODAS las subcuencas
        # Django traduce esto a: SELECT * FROM hidrografia_django_subcuencas
        l = EstacionesMonitoreoModel.objects.all()
        
        # Recorremos todos los resultados y convertimos cada uno a diccionario
        data = []
        for b in l:
            d = model_to_dict(b)
            d['geom'] = b.geom.wkt
            d['data_creation'] = d['data_creation'].strftime("%Y-%m-%d %H:%M:%S")
            data.append(d)  # Añade el diccionario a la lista
        
        return {'ok': True, 'message': f"Todas las estaciones de monitoreo: {len(data)}", 'data': data}
    
    def update(self, d:dict):
        cur=connection.cursor()
        query="select st_snaptogrid(st_geomfromtext(%s, %s),%s)"
        cur.execute(query, [d['geom'],EPSG_FOR_GEOMETRIES, ST_SNAP_PRECISION])
        snapped_wkb_geometry=cur.fetchall()[0][0]

        print(f'snapped_wkb_geometry: {snapped_wkb_geometry}')

        #now we can check if it is valid as before:
        g=GEOSGeometry(snapped_wkb_geometry, srid=EPSG_FOR_GEOMETRIES)
        if g.valid:
            print("Geometría válida")
        else:
            return {'ok': False, 'message':'Invalid geometry', 'data': None}
        
        #Now we can check if it intersects with another geomtry in the same layer
        #check if the geometry intersects any existing building
        query = """ 
            select id from hidrografia_django_subcuencas where st_within(
                %s,
                geom
            )
        """
        cur.execute(query, [snapped_wkb_geometry])
        r = cur.fetchall()

        if len(r) == 0:
            return {'ok': False, 'message': 'El punto no está dentro de ninguna subcuenca', 'data': None}
        

        #create the geometry with geos
        f=EstacionesMonitoreoModel.objects.filter(id=d['id'])
        l=list(f)
        if len(l)>0:
            b:EstacionesMonitoreoModel=l[0]
        else:
            return {'ok': False, 'message': f"No se encuentran estaciones de monitoreo con id {d['id']}", 'data': None}

        b.geom=g
        b.nombre=d['nombre']
        b.tipo=d['tipo']
        b.organismo=d["organismo"]
        b.estado=d["estado"]
        b.fecha_instalacion=d['fecha_instalacion']
        b.save()
        d=model_to_dict(b)
        d['geom']=g.wkt
        d['data_creation']=d['data_creation'].strftime("%Y-%m-%d %H:%M:%S")

        return {'ok':True, 'Message': f"Updated estaciones de monitoreo: {len(l)}",
                'data':[d]}
        
    def delete(self, d:dict):
        #create the geometry with geos
        f=EstacionesMonitoreoModel.objects.filter(id=d['id'])
        l=list(f)
        if len(l)<1:
            return {"ok":False, "Message": f"No se encuentra estaciones de monitoreo con id {d['id']}", "data":None}
        b=l[0]
        b.delete()
        return {'ok':True, 'Message': f"Estacion de monitoreo deleted: 1",
                'data':[{'id':d["id"]}]}

    
        
        
            
