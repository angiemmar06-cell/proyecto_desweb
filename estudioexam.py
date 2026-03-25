Ejercicio 1: Actualización por proximidad con ST_Distance
Contexto:
Tienes una tabla llamada cameras que representa cámaras de seguridad (puntos), con los campos id, status (texto, por defecto 'OFF') y geom. 
Ha ocurrido un incidente en unas coordenadas concretas y necesitas encender todas las cámaras que estén cerca.
Tu misión:
Crea una función llamada activate_cameras_nearby(incident_wkt: str, radius_meters: float) -> dict.
La función debe buscar todas las cámaras cuya geometría esté a una distancia igual o menor a radius_meters del punto incident_wkt (ST_Distance).
Debe actualizar el campo status de esas cámaras a 'ON'.
Debe devolver un diccionario indicando cuántas cámaras se han actualizado: {'ok': True, 'message': 'Cámaras activadas', 'updated_count': <num_filas>}.

#pyscopg

Import from myLib.settings import EPSG_CODE, SNAP_DISTANCE

#en lugar de connet porque no lo tengo, tengo esto:

class cameras():
		
	def __init__(self):
		self.conn = connect()
		self.cur = conn.cursor()
		
	def connect(self):
		conn = psycopg.connect(
            dbname='exam',
            user= 'postgres',
            password= 'postgres',
            host= 'postgis',
            port= 5432
            )
		return conn
			
	def disconnect(self):
		self.cur.close()
		self.conn.close()
        
		def activate_cameras_nearby(self, public):
			incident = public['geom']
			radius_meters = public['radio']
			
			
			# Comprobar geometría
			self.cur.execute("SELECT ST_IsValid(ST_SnapToGrid(ST_GeometryFromText(%s, %s), 0.0001))", [incident, EPSG_CODE])
			if not self.cur.fetchone()[0]:
				return {'ok': False, 'message': 'Error: La geometría no es válida.', 'data': None}
				
			# Si esa distancia es <= radius_meters, actualiza esa cámara
			cons = """
				UPDATE public.cameras
				SET status = 'ON'
				WHERE ST_Distance(
					geom,
					st_geomfromtext(%s, 25830)
				) <= %s
			"""
			self.cur.execute(cons, [incident, radius_meters])
			rows = cur.rowcount  
			self.conn.commit()
			cur.close()
			conn.close()
			
			return {'ok': True, 'message': 'Camaras activadas',
					'updated_count': rows}

#Django
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from miapp.models import Cameras as CamerasModel

class Camarasdjango:
    
    def update(self, d:dict):

        def activate_cameras_nearby(incident_wkt, radius_meters):
            # Crear geometría del incidente
            g = GEOSGeometry(incident_wkt, srid=25830)
            
            # Verificar que es válida
            if not g.valid:
                return {'ok': False, 'message': 'Geometria no valida', 'data': None}
            
            # Buscar cámaras cercanas al incidente
            # distance_lte = distancia menor o igual a
            # D(m=radius_meters) = distancia en metros
            camaras = CamerasModel.objects.filter(
                geom__distance_lte=(g, D(m=radius_meters))
            )
            
            # Actualizar todas las encontradas a 'ON'
            # .update() actualiza todas las filas del queryset de golpe
            rows = camaras.update(status='ON')
            
            return {'ok': True, 'message': 'Camaras activadas',
                    'updated_count': rows}

Ejercicio 2: INSERT con verificación de intersección
Tabla parcelas: 
    id 
    propietario (text), 
    uso (varchar 30), 
    geom (POLYGON, 25830)
Crea una función insert_parcela(d) que reciba un diccionario con los datos, verifique que la geometría es válida, 
que no se solapa con otras parcelas (st_relate T********), y si pasa todo, inserte la parcela. Devuelve {ok, message, data}.
Hazlo con psycopg y con Django Models.

#psycopg

from myLib.settings import EPSG_CODE, SNAP_DISTANCE

class parcelas():

	def __init__(self):
		self.conn = self.connect()
		self.cur = self.conn.cursor()
		
	def connect(self):
		conn = psycopg.connect(
            dbname='exam',
            user= 'postgres',
            password= 'postgres',
            host= 'postgis',
            port= 5432
            )
		return conn
			
	def disconnect(self):
		self.cur.close()
		self.conn.close()
        
    def insert_parcela(self,d):      
        #chequear la geometria si es valida y evitar errores con snaptogrid
        query = """
            select ST_isvalid(
                st_snaptogrid(
                    st_geomfromtext(%s, %s),
                    %s
                )
            ) as is_valid    
        """
        self.cur.execute(query, [d['geom'], EPSG_CODE, SNAP_DISTANCE])
        l = self.cur.fetchall()
        if not l [0][0]:
            self.cur.close()
            self.conn.close()
            return {'ok': False, 'message': 'La geometría no es válida', 'data': None}
        
        #verificar que no se solapan con otras parcelas
        query = """
            select id from d.parcelas where st_relate(
                geom,
                st_snaptogrid(
                    st_geomfromtext(%s, %s),
                    %s
                ),
                'T********'
            )
        """
        self.cur.execute(query, [d['geom'], EPSG_CODE, SNAP_DISTANCE])
        l = self.cur.fetchall()
        if len(l) > 0:
            print("Intersecta con otra")
            self.cur.close()
            self.conn.close()
            return {'ok': False, 'message': 'La geometría intersecta', 'data': None}
        # Paso 3: Escribir la sentencia SQL.
        cons = """
            INSERT INTO d.parcelas
                (propietario,uso, geom)
            VALUES
                (%s, %s,
                st_snaptogrid(st_geometryFromText(%s, %s), %s)) 
            RETURNING id
            """

        # Paso 4: Ejecutar la sentencia.
        # En vez de poner valores directos, leemos del diccionario d que nos pasaron
        self.cur.execute(cons,
                    [d['propietario'],
                     d['uso'],
                     d['geom'],
                     EPSG_CODE,
                     SNAP_DISTANCE 
                    ])
        # Paso 5: Confirmar los cambios.
        self.conn.commit()
        
        # Paso 6: Traer los resultados. fetchall() devuelve una lista con una tupla.
        l = self.cur.fetchall()
        
        # Paso 7: CERRAR cursor y conexión. FUNDAMENTAL.
  
        self.cur.close()
        self.conn.close()
        
        # Paso 8: Devolver resultado como diccionario con ok, message y data
        return {'ok': True, 'message': 'Data inserted', 'data': [{'id': l[0][0]}]}

#Django

#models.py

from django.db import models
from django.contrib.gis.db import models as gis_models

class ParcelasModel(models.Model):
    propietario = models.TextField(blank=True, null=True)
    uso = models.CharField(max_length= 30, blank=True, null=True)
    geom = gis_models.PolygonField(srid=25830,blank=True, null=True) 
    

# script parcelas.py (solo esto)
from django.contrib.gis.geos import GEOSGeometry
from django.forms.models import model_to_dict
from django.db import connection
from miapp.models import ParcelasModel
from djangoapi.settings import EPSG_FOR_GEOMETRIES, ST_SNAP_PRECISIO

class parcelas:
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
        query=""" 
            select id from d_django_parcelas where ST_relate(
                geom,
                %s,
                'T********'
            )
        """
        cur.execute(query, [snapped_wkb_geometry])
        r=cur.fetchall()

        if len(r)>0:
            return {'ok': False, 'message':'The geometry interior intersects with the following geometries id', 'data': r}

        d['geom']=g
        b=ParcelasModel(**d)
        b.save()
        d=model_to_dict(b)
        d['geom']=g.wkt
        return {'ok': True, 'message':'Parcelas inserted', 'data': [d]}
        
        
        
EJERCICIO 3: DELETE con verificación previa
Tabla zonas_verdes: id, nombre (text), superficie_m2 (float), geom (POLYGON, 25830)
Tabla arboles: id, especie (text), altura_m (float), geom (POINT, 25830)
Crea una función delete_zona_verde(d) que reciba {'id': X}. Antes de borrar la zona verde, debe verificar si hay árboles dentro de ella (st_within). 
Si hay árboles dentro, no borrar y devolver error indicando cuántos árboles quedarían huérfanos. Si no hay árboles dentro, borrar.

#Hazlo con psycopg.

import psycopg

def delete_zona_verde(d):
    conn = psycopg.connect(
        dbname='exam',
        user='postgres',
        password='postgres',
        host='postgis',
        port=5432
    )
    cur = conn.cursor()
    
    # Verificar si hay árboles dentro --> A dentro de B st_within(A, B)
    query = """
        SELECT id FROM d.arboles WHERE ST_within(
            geom,
            (SELECT geom FROM d.zonas_verdes WHERE id = %s)
        )
    """
    cur.execute(query, [d['id']])
    l = cur.fetchall()
    
    if len(l) > 0:
        cur.close()
        conn.close()
        return {'ok': False,
                'message': f'No se puede borrar, hay {len(l)} arboles dentro',
                'data': None}
    
    # Borrar
    cons = """DELETE FROM d.zonas_verdes WHERE id = %s"""
    cur.execute(cons, [d['id']])
    rows = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    
    return {'ok': True, 'message': 'Zona verde deleted',
            'data': [{'rows_deleted': rows}]}


EJERCICIO 4 UPDATE con cambio de geometría
Tabla tuberias: id, material (varchar 50), diametro_mm (float), estado (varchar 20), geom (LINESTRING, 25830)
Crea una función update_tuberia(d) que reciba un diccionario con todos los campos + id. Debe verificar que la geometría es válida, 
que no se cruza con otras tuberías (st_relate T********) excluyendo la propia, y actualizar. 
Devuelve {ok, message, data}.
Hazlo con psycopg y con Django Models.

#psycopg
import psycopg

def update_tuberia(d):
    conn = psycopg.connect(
        dbname='exam',
        user='postgres',
        password='postgres',
        host='postgis',
        port=5432
    )
    cur = conn.cursor()
    
    #chequear la geometria si es valida y evitar errores con snaptogrid
    query = """
        select ST_isvalid(
            st_snaptogrid(
                st_geomfromtext(%s, %s),
                %s
            )
        ) as is_valid    
    """
    cur.execute(query, [d['geom'], EPSG_CODE, SNAP_DISTANCE])
    l = cur.fetchall()
    if not l [0][0]:
        cur.close()
        conn.close()
        return {'ok': False, 'message': 'La geometría no es válida', 'data': None}
    
    #verificar que no se cruza
    query = """
        select id from d.tuberias where ST_relate(
            geom,
            st_snaptogrid(
                st_geomfromtext(%s, %s),
                %s
            ),
            'T********'
        ) and id != %s
    """
    cur.execute(query, [d['geom'], EPSG_CODE, SNAP_DISTANCE, d['id']])
    l = cur.fetchall()
    if len(l) > 0:
        cur.close()
        conn.close()
        return {'ok': False, 'message': 'Las tuberias se intersectan', 'data': None}
    cons="""
        UPDATE
            d.tuberias
        SET 
            (material, diametro_mm, estado, geom) = ROW(%s, %s, %s, st_snaptogrid(st_geometryFromText(%s, %s), %s))  
        WHERE
            id = %s
        """
   
    cur.execute(cons,
                [d['material'],           
                d['diametro_mm'],             
                d['estado'],      
                d['geom'],             
                EPSG_CODE,
                SNAP_DISTANCE,
                d['id']
                ])
    rows = cur.rowcount # Imprime cuántas filas se modificaron (debería ser 1)
    conn.commit() # Confirma los cambios. Sin esto el UPDATE no se guarda
    cur.close()
    conn.close()
    return {'ok': True, 'message': 'Data updated', 'data': [{'rows_updated': rows}]}
    
    
    
    
#Django

#models.py

from django.db import models
from django.contrib.gis.db import models as gis_models

class TuberiasModel(models.Model):
    material = models.CharField(max_length= 50, blank=True, null=True)
    diametro_mm = models.FloatField(blank=True, null=True)
    estado = models.CharField(max_length= 20, blank=True, null=True)
    geom = gis_models.LineStringField(srid=25830,blank=True, null=True) 
    

# script tuberias.py
from django.contrib.gis.geos import GEOSGeometry
from django.forms.models import model_to_dict
from django.db import connection
from miapp.models import TuberiasModel
from djangoapi.settings import EPSG_FOR_GEOMETRIES, ST_SNAP_PRECISION

class Tuberias:
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
        query=""" 
            select id from d_django_tuberias where ST_relate(
                geom,
                %s,
                'T********'
            ) and id != %s
        """
        cur.execute(query, [snapped_wkb_geometry, d['id']])
        r=cur.fetchall()

        if len(r)>0:
            return {'ok': False, 'message': 'La geometría intersecta con otra', 'data': r}

        #create the geometry with geos
        f=TuberiasModel.objects.filter(id=d['id'])
        l=list(f)
        if len(l)>0:
            b:TuberiasModel=l[0]
        else:
            return {'ok': False, 'message': f"No Tuberias found with id {d['id']}", 'data': None}

        b.geom=g
        b.material=d['material']
        b.diametro_mm=d['diametro_mm']
        b.estado=d["estado"]
        b.save()
        d=model_to_dict(b)
        d['geom']=g.wkt

        return {'ok':True, 'Message': f"Updated Tuberias: {len(l)}",
                'data':[d]}
                
EJERCICIO 4: SELECT con filtro geográfico
Tabla sensores: id, tipo (varchar 20), valor_actual (float), geom (POINT, 25830)
Crea una función sensores_dentro_zona(zona_wkt) que reciba un polígono en WKT y devuelva todos los sensores que estén dentro de ese polígono (st_within). Devuelve {ok, message, data} con la lista de sensores encontrados.
Hazlo con psycopg.

EJERCICIO 5: INSERT de punto con verificación st_within
Tabla hidrantes: id, codigo (varchar 10), presion_bar (float), geom (POINT, 25830)
Tabla distritos: id, nombre (text), geom (POLYGON, 25830)
Crea una función insert_hidrante(d) que reciba un diccionario con los datos del hidrante. Debe verificar que el punto está dentro de algún distrito (st_within). Si no está dentro de ninguno, rechazar. Si está dentro, insertar.
Hazlo con psycopg y con Django Models.

EJERCICIO A: Buscar ríos contaminados cerca de una ciudad
Tabla rios: id, nombre (text), nivel_contaminacion (float), geom (LINESTRING, 25830)
Crea una función rios_contaminados_cerca(ciudad_wkt: str, radio_km: float, umbral_contaminacion: float) -> dict
Debe buscar todos los ríos que estén a menos de radio_km kilómetros del punto ciudad_wkt Y que tengan nivel_contaminacion mayor al umbral_contaminacion. Devuelve {ok, message, data} con la lista de ríos encontrados.
Hazlo con psycopg.

EJERCICIO B: Insertar un pozo solo si está lejos de otros pozos
Tabla pozos: id, profundidad_m (float), caudal_ls (float), estado (varchar 20), geom (POINT, 25830)
Crea una función insert_pozo(d: dict, distancia_minima: float) -> dict
Debe insertar un pozo solo si NO existe otro pozo a menos de distancia_minima metros (ST_Distance). Si hay algún pozo demasiado cerca, rechazar y devolver los ids de los pozos cercanos.
Hazlo con psycopg y Django.

EJERCICIO C: Desactivar sensores dentro de una zona de riesgo
Tabla sensores: id, tipo (varchar 20), activo (boolean), geom (POINT, 25830)
Crea una función desactivar_sensores_en_zona(zona_wkt: str) -> dict
Recibe un polígono WKT que representa una zona de riesgo. Debe buscar todos los sensores activos (activo = true) que estén dentro de esa zona (ST_Within) y cambiarles activo a false. Devuelve cuántos sensores se desactivaron.
Hazlo con psycopg.

EJERCICIO D: Mover una estación y verificar que sigue dentro de su zona
Tabla estaciones: id, nombre (text), zona_id (integer), geom (POINT, 25830)
Tabla zonas: id, nombre (text), geom (POLYGON, 25830)
Crea una función mover_estacion(d: dict) -> dict que reciba {'id': X, 'geom': 'POINT(...)'}.
Debe buscar la estación por id, obtener su zona_id, verificar que la nueva ubicación sigue dentro de esa misma zona (ST_Within), y si está dentro actualizar la geometría. Si no está dentro, rechazar.
Hazlo con psycopg.

EJERCICIO E: Calcular estadísticas de una subcuenca
Tabla subcuencas: id, nombre (text), geom (POLYGON, 25830)
Tabla estaciones: id, tipo (varchar 20), valor_medicion (float), geom (POINT, 25830)
Crea una función estadisticas_subcuenca(d: dict) -> dict que reciba {'id': X}.
Debe buscar la subcuenca por id, contar cuántas estaciones hay dentro (ST_Within), y calcular el promedio de valor_medicion de esas estaciones. Devuelve {ok, message, data: [{'num_estaciones': N, 'promedio_medicion': X}]}.
Hazlo con psycopg.