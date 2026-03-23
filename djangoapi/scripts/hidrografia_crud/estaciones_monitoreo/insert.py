# Importa la función connect desde myLib/connect.py para poder conectarnos a la base de datos
from myLib.connect import connect
# Importa el código EPSG (25830) desde myLib/settings.py. Es el sistema de coordenadas de España
from myLib.settings import EPSG_CODE, SNAP_DISTANCE

# La función recibe d, que es un diccionario con los datos de la estación
# Ejemplo: {'nombre': 'Estación Turia Este', 'tipo': 'calidad', ...}
def insert(d):
    # Paso 1: Abrir conexión con la base de datos. Es como abrir la puerta de la base de datos    
    conn = connect()
    # Paso 2: Crear un cursor. Es el dedo que ejecuta las sentencias SQL.
    # Sin cursor no puedes hacer nada en la base de datos
    cur = conn.cursor()
    # Paso 3: Escribir la sentencia SQL.
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
    
    # que este dentro
    # Si NO está dentro de ninguna subcuenca, rechazar
    query = """
        select id from d.subcuencas where ST_within(
            st_snaptogrid(st_geomfromtext(%s, %s), %s),
            geom
        )
    """
    # Si len(l) == 0 → no está dentro de ninguna → rechazar
    cur.execute(query, [d['geom'], EPSG_CODE, SNAP_DISTANCE])
    l = cur.fetchall()
    if len(l) == 0:
        cur.close()
        conn.close()
        return {'ok': False, 'message': 'No se encuentra dentro de una subcuenca', 'data': None}
    cons = """
        INSERT INTO d.estaciones_monitoreo
            (nombre, tipo, organismo, estado, fecha_instalacion, geom)
        VALUES
            (%s, %s, %s, %s, %s,
            st_snaptogrid(st_geomfromtext(%s, %s), %s)) 
        RETURNING id
        """
    # Los %s son "huecos" que se rellenan después con los valores reales.
    # st_geometryFromText convierte el texto 'POINT((...))' en una geometría real
    # que PostGIS entiende. Necesita dos cosas: el texto WKT y el código EPSG
    # RETURNING id le dice a PostgreSQL: "después de insertar, dime qué id le asignaste"
    
    # Paso 4: Ejecutar la sentencia.
    # En vez de poner valores directos, leemos del diccionario d que nos pasaron
    cur.execute(cons,
                [d['nombre'],              
                 d['tipo'],                
                 d['organismo'],           
                 d['estado'],              
                 d['fecha_instalacion'],   
                 d['geom'],                
                 EPSG_CODE,
                 SNAP_DISTANCE
                ])                 
    # Paso 5: Confirmar los cambios.
    conn.commit() # Sin commit los datos NO se guardan. Es como darle a "guardar" en un documento
    
    # Paso 6: Traer los resultados. fetchall() devuelve una lista con una tupla.
    l = cur.fetchall() # es como decirle al cursor: "pásame eso que tienes guardado"
    # IMPORTANTE: solo puedes llamar fetchall() UNA VEZ por cada execute()
    
    # Paso 7: CERRAR cursor y conexión. FUNDAMENTAL.
    # Si no cierras, la conexión queda abierta. PostgreSQL tiene un límite de 100
    # conexiones. Si se acaban, nadie más puede conectarse
    cur.close()
    conn.close()
    
    # Paso 8: Devolver resultado como diccionario con ok, message y data
    # En vez de solo imprimir, devolvemos información útil para quien llame la función
    return {'ok': True, 'message': 'Data inserted', 'data': [{'id': l[0][0]}]}

# Los datos ya no están dentro de la función, vienen de fuera en un diccionario
# Así la función sirve para insertar CUALQUIER estación, no solo una específica


