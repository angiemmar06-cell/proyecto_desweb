from myLib.connect import connect

def delete(d):
    conn = connect()
    cur = conn.cursor()
    # DELETE FROM elimina una fila de la tabla
    # WHERE id = %s indica CUÁL fila borrar. Sin WHERE borraría TODAS las filas
    cons = """
        DELETE FROM
            d.subcuencas 
        WHERE
            codigo = %s
        """
    # solo 1 valor porque solo hay 1 %s en la sentencia del id
    cur.execute(cons, [d['codigo']])
    rows = cur.rowcount  # Guardar ANTES de cerrar el cursor
    conn.commit()
    cur.close()
    conn.close()
    return {'ok': True, 'message': 'Data deleted', 'data': [{'rows_deleted': rows}]}

#print(delete({'id': 37}))
#print("Deleted")