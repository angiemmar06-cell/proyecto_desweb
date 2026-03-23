from myLib.connect import connect
from myLib.settings import EPSG_CODE, SNAP_DISTANCE

# La función recibe d, que es un diccionario con los datos a actualizar + el id
def update(d):
    conn = connect()
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
        select id from d.subcuencas where ST_relate(
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
        print("Intersecta con otra subcuenca")
        cur.close()
        conn.close()
        return {'ok': False, 'message': 'La geometría intersecta con otra subcuenca', 'data': None}
    cons = """
        UPDATE
            d.subcuencas 
        SET 
            (nombre, codigo, area_km2, perimetro_km, uso_suelo, geom) = ROW(%s, %s, %s, %s, %s, st_snaptogrid(st_geometryFromText(%s, %s), %s))    
        WHERE
            id = %s
        """
    # 8 valores porque hay 8 %s en la sentencia:
    # nombre, codigo, area_km2, perimetro_km, uso_suelo, geom_wkt, epsg, id
    cur.execute(cons,
                [d['nombre'],
                 d['codigo'],
                 d['area_km2'],
                 d['perimetro_km'],
                 d['uso_suelo'],
                 d['geom'],
                 EPSG_CODE,
                 SNAP_DISTANCE,
                 d['id']
                ])
    rows = cur.rowcount  # Guardar ANTES de cerrar el cursor
    conn.commit()
    cur.close()
    conn.close()
    return {'ok': True, 'message': 'Data updated', 'data': [{'rows_updated': rows}]}

#print(update(d))
#print("Updated")