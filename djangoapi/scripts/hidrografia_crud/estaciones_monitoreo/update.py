from myLib.connect import connect
# Importa EPSG_CODE (25830) para usarlo en la conversión de geometría
from myLib.settings import EPSG_CODE, SNAP_DISTANCE

# La función recibe d, que es un diccionario con los datos a actualizar + el id
def update(d):
    conn = connect()
    cur = conn.cursor()
    # UPDATE modifica una fila que ya existe
    # ROW() agrupa todos los valores nuevos en una sola expresión
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
        UPDATE
            d.estaciones_monitoreo
        SET 
            (nombre, tipo, organismo, estado, fecha_instalacion, geom) = ROW(%s, %s, %s, %s, %s, st_snaptogrid(st_geomfromtext(%s, %s), %s))    
        WHERE
            id = %s
        """
    # WHERE id = %s indica CUÁL fila modificar. Sin WHERE modificaría TODAS las filas
    
    # 8 valores porque hay 8 %s en la sentencia:
    # nombre, tipo, organismo, estado, fecha_instalacion, geom_wkt, epsg, id
    cur.execute(cons,
                [d['nombre'],
                 d['tipo'],
                 d['organismo'],
                 d['estado'],
                 d['fecha_instalacion'],
                 d['geom'],
                 EPSG_CODE,
                 SNAP_DISTANCE,
                 d['id']
                ])
    rows = cur.rowcount  # Guardar ANTES de cerrar el cursor
    conn.commit() # Confirma los cambios. Sin esto el UPDATE no se guarda
    cur.close()
    conn.close()
    return {'ok': True, 'message': 'Data updated', 'data': [{'rows_updated': rows}]}
