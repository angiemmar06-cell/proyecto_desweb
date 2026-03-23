from myLib.connect import connect
from psycopg.rows import dict_row

# Función select: busca subcuencas por uso de suelo
def select(d, asDict=False):
    conn = connect()
    if asDict:
        cur = conn.cursor(row_factory=dict_row)
    else:
        cur = conn.cursor()

    cons = """
        SELECT 
            id, nombre, codigo, area_km2, perimetro_km, uso_suelo, st_astext(geom)
        FROM 
            d.subcuencas 
        WHERE
            uso_suelo = %s
        """
    cur.execute(cons, [d['uso_suelo']])
    l = cur.fetchall()
    cur.close()
    conn.close()
    return {'ok': True, 'message': f"Subcuencas seleccionadas: {len(l)}", 'data': l}

# Función selectone: busca UNA subcuenca por su id
def selectone(d, asDict=False):
    conn = connect()
    if asDict:
        cur = conn.cursor(row_factory=dict_row)
    else:
        cur = conn.cursor()

    cons = """
        SELECT 
            id, nombre, codigo, area_km2, perimetro_km, uso_suelo, st_astext(geom)
        FROM 
            d.subcuencas 
        WHERE
            id = %s
        """
    cur.execute(cons, [d['id']])
    l = cur.fetchall()
    cur.close()
    conn.close()
    return {'ok': True, 'message': f"Subcuencas encontradas: {len(l)}", 'data': l}

# Función selectall: trae TODAS las subcuencas, no necesita diccionario
def selectall(asDict=False):
    conn = connect()
    if asDict:
        cur = conn.cursor(row_factory=dict_row)
    else:
        cur = conn.cursor()

    cons = """
        SELECT 
            id, nombre, codigo, area_km2, perimetro_km, uso_suelo, st_astext(geom)
        FROM 
            d.subcuencas
        """
    cur.execute(cons)
    l = cur.fetchall()
    cur.close()
    conn.close()
    return {'ok': True, 'message': f"Todas las subcuencas: {len(l)}", 'data': l}

# Pruebas
#print("--" * 15, "Select - por uso de suelo", "--" * 15)
#print(select({'uso_suelo': 'Mixto'}))

#print("--" * 15, "Selectall - TODAS", "--" * 15)
#print(selectall())

#print("--" * 15, "Selectone - una sola", "--" * 15)
#print(selectone({'id': 1}, asDict=True))