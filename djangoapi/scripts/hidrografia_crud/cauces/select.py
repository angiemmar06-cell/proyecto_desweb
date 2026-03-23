from myLib.connect import connect
# Importa dict_row para poder recibir los resultados como diccionarios en vez de tuplas
from psycopg.rows import dict_row

# asDict=False es un valor por defecto. Si llamas select() sin parámetro, asDict será False
# Si llamas select(asDict=True), los resultados vendrán como diccionarios

#Funcion select
def select(d, asDict=False):
    # Abrir conexión con la base de datos.
    conn=connect()

    if asDict:
        # Cursor especial que devuelve cada fila como diccionario: {'id': 1, 'nombre': '...'}
        #The rows are dicts
        cur=conn.cursor(row_factory=dict_row)
    else:
        # Cursor normal que devuelve cada fila como tupla: (1, '...')
        #Te rows are tuples
        cur=conn.cursor()

    cons="""
        SELECT 
            id, nombre, tipo, longitud_km, caudal_medio, estado_ecologico, st_astext(geom)
        FROM 
            d.cauces
        WHERE
            caudal_medio>%s and caudal_medio <%s
        """
    cur.execute(cons, [d['caudal_minimo'], d['caudal_maximo']])#es la orden que le doy al mensajero, el mensajero es el cursor
    # Le dices a la base de datos: "inserta / selecciona este cauce y dime qué id le diste"
    # En este momento el cursor TIENE el resultado (el id) pero tú NO, Si intentas usar el id aquí, no puedes
    # Ahora le pides al cursor que te pase el resultado con ferchall
    l=cur.fetchall() # devuelve una lista con una tupla dentro con el id: [(25,)], es cuando le digo al mensajero que me de la orden
    #print(l)
    #print('First row:')
    #print(l[0])
    #conn.commit() -->no necesario en select
    cur.close()
    conn.close()
    return {'ok':True, 'Message': f"Cauces Seleccionados: {len(l)}", 'data':l}

#Funcion selectall (que me muestre todos)
def selectall(asDict=False):
    # Abrir conexión con la base de datos.
    conn=connect()

    if asDict:
        # Cursor especial que devuelve cada fila como diccionario: {'id': 1, 'nombre': '...'}
        #The rows are dicts
        cur=conn.cursor(row_factory=dict_row)
    else:
        # Cursor normal que devuelve cada fila como tupla: (1, '...')
        #Te rows are tuples
        cur=conn.cursor()

    cons="""
        SELECT 
            id, nombre, tipo, longitud_km, caudal_medio, estado_ecologico, st_astext(geom)
        FROM 
            d.cauces
        WHERE
            id>0
        """
    cur.execute(cons)#es la orden que le doy al mensajero, el mensajero es el cursor
    # Le dices a la base de datos: "inserta / selecciona este cauce y dime qué id le diste"
    # En este momento el cursor TIENE el resultado (el id) pero tú NO, Si intentas usar el id aquí, no puedes
    # Ahora le pides al cursor que te pase el resultado con ferchall
    l=cur.fetchall() # devuelve una lista con una tupla dentro con el id: [(25,)], es cuando le digo al mensajero que me de la orden
    #print(l)
    #print('First row:')
    #print(l[0])
    #conn.commit()
    cur.close()
    conn.close()
    
    return {'ok':True, 'Message': f"Todos los Cauces: {len(l)}", 'data':l}

#Funcion selectone (muestra one, el que quiera)
def selectone(d, asDict=False):
    # Abrir conexión con la base de datos.
    conn=connect()

    if asDict:
        # Cursor especial que devuelve cada fila como diccionario: {'id': 1, 'nombre': '...'}
        #The rows are dicts
        cur=conn.cursor(row_factory=dict_row)
    else:
        # Cursor normal que devuelve cada fila como tupla: (1, '...')
        #Te rows are tuples
        cur=conn.cursor()

    cons="""
        SELECT 
            id, nombre, tipo, longitud_km, caudal_medio, estado_ecologico, st_astext(geom)
        FROM 
            d.cauces
        WHERE
            id = %s
        """
    cur.execute(cons, [d['id']])#es la orden que le doy al mensajero, el mensajero es el cursor
    # Le dices a la base de datos: "inserta / selecciona este cauce y dime qué id le diste"
    # En este momento el cursor TIENE el resultado (el id) pero tú NO, Si intentas usar el id aquí, no puedes
    # Ahora le pides al cursor que te pase el resultado con ferchall
    l=cur.fetchall() # devuelve una lista con una tupla dentro con el id: [(25,)], es cuando le digo al mensajero que me de la orden
    #print(l)
    #print('First row:')
    #print(l[0])
    #conn.commit()
    cur.close()
    conn.close()
    return {'ok':True, 'Message': f"Cauces encontrados: {len(l)}", 'data':l}

#prints
#print("--"*15, "Select - especificas", "--"*15)
#print(select({'caudal_minimo': 1, 'caudal_maximo': 10}))


#print("--"*15, "Selectall - TODAS", "--"*15)
#print(selectall())

#print("--"*15, "Selectone - una sola", "--"*15)
#print(selectone({'id':7}, asDict=True))