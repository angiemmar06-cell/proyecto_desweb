import sys

#tabla de Cauces
from cauces.insert import insert as insert_cauces
from cauces.select import select as select_cauces
from cauces.select import selectall as selectall_cauces
from cauces.select import selectone as selectone_cauces
from cauces.update import update as update_cauces
from cauces.delete import delete as delete_cauces

#Tabla de estaciones_monitoreo
from estaciones_monitoreo.insert import insert as insert_estaciones_monitoreo
from estaciones_monitoreo.select import select as select_estaciones_monitoreo
from estaciones_monitoreo.select import selectall as selectall_estaciones_monitoreo
from estaciones_monitoreo.select import selectone as selectone_estaciones_monitoreo
from estaciones_monitoreo.update import update as update_estaciones_monitoreo
from estaciones_monitoreo.delete import delete as delete_estaciones_monitoreo

#Tabla subcuencas
from subcuencas.insert import insert as insert_subcuencas
from subcuencas.select import select as select_subcuencas
from subcuencas.select import selectall as selectall_subcuencas
from subcuencas.select import selectone as selectone_subcuencas
from subcuencas.update import update as update_subcuencas
from subcuencas.delete import delete as delete_subcuencas

def main():
    # sys.argv[0] es siempre el nombre del archivo (main.py)
    # Por eso verificamos que haya al menos 3 elementos (nombre + p1 + p2)
    if len(sys.argv) == 3:
        tableName = sys.argv[1]
        functionName = sys.argv[2]     
    else:
        print("Error: Debes dar dos parámetros: tableName y functionName")
        sys.exit(0)

    if tableName not in ["cauces", "subcuencas", "estaciones_monitoreo"]:
        print("Error: Las tablas disponibles son: cauces, subcuencas, estaciones_monitoreo")
        sys.exit(0)
    
    if functionName not in ["insert", "select", "selectall", "selectone", "update", "delete"]:
        print("Error: Las funciones disponibles son: insert, select, selectone, selectall, update, delete")
        sys.exit(0)

    #Tabla Cauces
    if tableName == "cauces":
        if functionName == "insert":
            d = {
                'nombre': 'Río Turia',
                'tipo': 'rio',
                'longitud_km': 280.5,
                'caudal_medio': 15.3,
                'estado_ecologico': 'Bueno',
                'geom': 'LINESTRING(720000 4372000, 722000 4373000, 724000 4373500, 726000 4374000)'
            }
            print(insert_cauces(d))
        elif functionName == "select":
            print(select_cauces({'caudal_minimo': 1, 'caudal_maximo': 10}))
        elif functionName == "selectall":
            print(selectall_cauces(asDict=True))
        elif functionName == "selectone":
            print(selectone_cauces({'id': 1}, asDict=True))
        elif functionName == "update":
            d = {
                'id': 1,
                'nombre': 'Río Turia',
                'tipo': 'rio',
                'longitud_km': 280.5,
                'caudal_medio': 15.3,
                'estado_ecologico': 'Bueno',
                'geom': 'LINESTRING(720000 4372000, 722000 4373000, 724000 4373500, 726000 4374000)'
            }
            print(update_cauces(d))
        elif functionName == "delete":
            print(delete_cauces({'id': 9}))
            
    #Tabla Subcuencas
    elif tableName == "subcuencas":
        if functionName == "insert":
            d = {
                'nombre': 'Barranco de Chiva',
                'codigo': 'SC004',
                'area_km2': 215.6,
                'perimetro_km': 72.3,
                'uso_suelo': 'Forestal',
                'geom': 'POLYGON((718000 4366000, 721000 4366000, 721000 4368500, 718000 4368500, 718000 4366000))'
            }
            print(insert_subcuencas(d))
        elif functionName == "select":
            print(select_subcuencas({'uso_suelo': 'Mixto'}))
        elif functionName == "selectall":
            print(selectall_subcuencas(asDict=True))
        elif functionName == "selectone":
            print(selectone_subcuencas({'id': 1}, asDict=True))
        elif functionName == "update":
            d = {
                'id': 1,
                'nombre': 'Río Turia',
                'codigo': 'SC001',
                'area_km2': 6393.8,
                'perimetro_km': 280,
                'uso_suelo': 'Urbano',
                'geom': 'POLYGON((720000 4370000, 725000 4370000, 725000 4375000, 720000 4375000, 720000 4370000))'
            }
            print(update_subcuencas(d))
        elif functionName == "delete":
            print(delete_subcuencas({'codigo': 'SC003'}))
    
    #Tabla estaciones_monitoreo
    elif tableName == "estaciones_monitoreo":
        if functionName == "insert":
            d = {
                'nombre': 'Estación Turia Este',
                'tipo': 'calidad',
                'organismo': 'Ayuntamiento Valencia',
                'estado': 'Mantenimiento',
                'fecha_instalacion': '2020-09-01',
                'geom': 'POINT(724500 4371500)'
            }
            print(insert_estaciones_monitoreo(d))
        elif functionName == "select":
            print(select_estaciones_monitoreo({'tipo': 'calidad'}))
        elif functionName == "selectall":
            print(selectall_estaciones_monitoreo(asDict=True))
        elif functionName == "selectone":
            print(selectone_estaciones_monitoreo({'id': 1}, asDict=True))
        elif functionName == "update":
            d = {
                'id': 5,
                'nombre': 'Estación Turia Este',
                'tipo': 'calidad',
                'organismo': 'Ayuntamiento Valencia',
                'estado': 'En Reparación',
                'fecha_instalacion': '2020-09-01',
                'geom': 'POINT(724500 4371500)'
            }
            print(update_estaciones_monitoreo(d))
        elif functionName == "delete":
            print(delete_estaciones_monitoreo({'id': 1}))
    

if __name__ == "__main__":
    main()