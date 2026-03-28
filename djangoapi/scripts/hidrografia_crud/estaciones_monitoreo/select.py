from myLib.connect import connect
# Importa dict_row para poder recibir los resultados como diccionarios en vez de tuplas
from psycopg.rows import dict_row

# Función select: busca estaciones por tipo (aforo, calidad, pluviometrica)
def select(d, asDict=False):
    conn = connect()
    if asDict:
        cur = conn.cursor(row_factory=dict_row)
    else:
        cur = conn.cursor()

    cons = """
        SELECT 
            id, nombre, tipo, organismo, estado, fecha_instalacion, st_astext(geom)
        FROM 
            d.estaciones_monitoreo 
        WHERE
            tipo = %s
        """
    cur.execute(cons, [d['tipo']])
    l = cur.fetchall()
    cur.close()
    conn.close()
    return {'ok': True, 'message': f"Estaciones seleccionadas: {len(l)}", 'data': l}

# Función selectone: busca UNA estación por su id
def selectone(d, asDict=False):
    conn = connect()
    if asDict:
        cur = conn.cursor(row_factory=dict_row)
    else:
        cur = conn.cursor()

    cons = """
        SELECT 
            id, nombre, tipo, organismo, estado, fecha_instalacion, st_astext(geom)
        FROM 
            d.estaciones_monitoreo 
        WHERE
            id = %s
        """
    cur.execute(cons, [d['id']])
    l = cur.fetchall()
    cur.close()
    conn.close()
    return {'ok': True, 'message': f"Estaciones encontradas: {len(l)}", 'data': l}

# Función selectall: trae TODAS las estaciones, no necesita diccionario
def selectall(asDict=False):
    conn = connect()
    if asDict:
        cur = conn.cursor(row_factory=dict_row)
    else:
        cur = conn.cursor()

    cons = """
        SELECT 
            id, nombre, tipo, organismo, estado, fecha_instalacion, st_astext(geom)
        FROM 
            d.estaciones_monitoreo
        """
    cur.execute(cons)
    l = cur.fetchall()
    cur.close()
    conn.close()
    return {'ok': True, 'message': f"Todas las estaciones: {len(l)}", 'data': l}

# Prints
# print("--" * 15, "Select - por tipo", "--" * 15)
# print(select({'tipo': 'calidad'}))

# print("--" * 10, "Selectall - TODAS", "--" * 10)
# print(selectall())

# print("--" * 10, "Selectone - una sola", "--" * 10)
# print(selectone({'id': 1}, asDict=True))