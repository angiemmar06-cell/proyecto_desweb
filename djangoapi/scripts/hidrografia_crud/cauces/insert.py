# Importa la función connect desde myLib/connect.py para poder conectarnos a la base de datos
from myLib.connect import connect
# Importa el código EPSG (25830) desde myLib/settings.py. Es el sistema de coordenadas de España
from myLib.settings import EPSG_CODE, SNAP_DISTANCE

# La función recibe d, que es un diccionario con los datos del cauce
# Ejemplo: {'nombre': 'Río Turia', 'tipo': 'rio', 'longitud_km': 280.5, ...}
def insert(d):
    # Paso 1: Abrir conexión con la base de datos. Es como abrir la puerta de la base de datos    
    conn = connect()
    # Paso 2: Crear un cursor. Es el dedo que ejecuta las sentencias SQL.
    # Sin cursor no puedes hacer nada en la base de datos
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
    
    #verificar que no se solapan con otras subcuencas
    query = """
        select id from d.cauces where ST_relate(
            geom,
            st_snaptogrid(
                st_geomfromtext(%s, %s),
                %s
            ),
            'T********'
        )
    """
    cur.execute(query, [d['geom'], EPSG_CODE, SNAP_DISTANCE])
    l = cur.fetchall()
    if len(l) > 0:
        cur.close()
        conn.close()
        return {'ok': False, 'message': 'La geometría intersecta con otro cauce', 'data': None}
    # Paso 3: Escribir la sentencia SQL.
    cons = """
        INSERT INTO d.cauces
            (nombre, tipo, longitud_km, caudal_medio, estado_ecologico, geom)
        VALUES
            (%s, %s, %s, %s, %s,
            st_snaptogrid(st_geometryFromText(%s, %s), %s))
        RETURNING id
        """
    # Los %s son "huecos" que se rellenan después con los valores reales.
    # st_geometryFromText convierte el texto 'LINESTRING((...))' en una geometría real
    # que PostGIS entiende. Necesita dos cosas: el texto WKT y el código EPSG
    # RETURNING id le dice a PostgreSQL: "después de insertar, dime qué id le asignaste"
    
    # Paso 4: Ejecutar la sentencia.
    # En vez de poner valores directos, leemos del diccionario d que nos pasaron
    cur.execute(cons,
                [d['nombre'],           
                 d['tipo'],             
                 d['longitud_km'],      
                 d['caudal_medio'],     
                 d['estado_ecologico'], 
                 d['geom'],             # → texto WKT para st_geometryFromText
                 EPSG_CODE,
                 SNAP_DISTANCE              
                ])
    # Paso 5: Confirmar los cambios.
    conn.commit() # Sin commit los datos NO se guardan. Es como darle a "guardar" en un documento
    
    # Paso 6: Traer los resultados. fetchall() devuelve una lista con una tupla.
    l = cur.fetchall() # es como decirle al cursor: "pásame eso que tienes guardado". Y el cursor te lo entrega como una lista.
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
# Así la función sirve para insertar CUALQUIER cauce, no solo uno específico
