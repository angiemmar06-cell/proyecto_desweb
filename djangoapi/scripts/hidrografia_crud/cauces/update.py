from myLib.connect import connect
# Importa EPSG_CODE (25830) para usarlo en la conversión de geometría
from myLib.settings import EPSG_CODE, SNAP_DISTANCE

def update(d):
    conn=connect()
    cur=conn.cursor()
    # UPDATE modifica una fila que ya existe
    # ROW() agrupa todos los valores nuevos en una sola expresión
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
    
    #verificar que no se solapan
    query = """
        select id from d.cauces where ST_relate(
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
        return {'ok': False, 'message': 'La geometría intersecta con otro cauce', 'data': None}
    cons="""
        UPDATE
            d.cauces
        SET 
            (nombre, tipo, longitud_km, caudal_medio, estado_ecologico, geom) = ROW(%s, %s, %s, %s, %s, st_snaptogrid(st_geometryFromText(%s, %s), %s))  
        WHERE
            id = %s
        """
    # WHERE id = %s indica CUÁL fila modificar. Sin WHERE modificaría TODAS las filas
    
    # 8 valores porque hay 8 %s en la sentencia:
    # nombre, codigo, area_km2, perimetro_km, uso_suelo, geom_wkt, epsg, id
    
    cur.execute(cons,
                [d['nombre'],           
                d['tipo'],             
                d['longitud_km'],      
                d['caudal_medio'],     
                d['estado_ecologico'], 
                d['geom'],             
                EPSG_CODE,
                SNAP_DISTANCE,
                d['id']
                ])
    #excute --> ejecuta la sentencia y guarda el resultado dentro del cursor. 
    rows = cur.rowcount # Imprime cuántas filas se modificaron (debería ser 1)
    conn.commit() # Confirma los cambios. Sin esto el UPDATE no se guarda
    cur.close()
    conn.close()
    return {'ok': True, 'message': 'Data updated', 'data': [{'rows_updated': rows}]}




