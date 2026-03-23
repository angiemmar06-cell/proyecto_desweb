# Importa la función connect para conectarse a la base de datos
from myLib.connect import connect

def delete(d):
    conn = connect()
    cur = conn.cursor()
    # DELETE FROM elimina una fila de la tabla
    # WHERE id = %s indica CUÁL fila borrar. Sin WHERE borraría TODAS las filas
    cons = """
        DELETE FROM
            d.estaciones_monitoreo
        WHERE
            id = %s
        """
    # solo 1 valor porque solo hay 1 %s en la sentencia del id
    cur.execute(cons, [d['id']]) # envía la sentencia SQL a la base de datos para que la ejecute.
    # Esto se hace por seguridad, no dar los valores directos, se le llama SQL injection usando 
    # %s y la lista psycopg protege los valores automaticamente
    rows = cur.rowcount  # Guardar ANTES de cerrar el cursor
    conn.commit() # Confirma el borrado. Sin esto la fila NO se borra realmente
    cur.close()
    conn.close()
    return {'ok': True, 'message': 'Data deleted', 'data': [{'rows_deleted': rows}]}

#print(delete({'id': 5}))
#print("Deleted")