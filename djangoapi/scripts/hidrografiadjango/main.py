from scripts.hidrografiadjango.subcuencas import Subcuencas
from scripts.hidrografiadjango.cauces import Cauces
from scripts.hidrografiadjango.estaciones_monitoreo import EstacionesMonitoreo

def run(*args):
    s = Subcuencas()
    c = Cauces()
    e = EstacionesMonitoreo()
    
    if len(args) < 2:
        print("Error: Debes dar dos parámetros: tabla y función")
        return
    
    tableName = args[0]
    functionName = args[1]
    
    if tableName not in ["cauces", "subcuencas", "estaciones_monitoreo"]:
        print("Error: Las tablas disponibles son: cauces, subcuencas, estaciones_monitoreo")
        return
    
    if functionName not in ["insert", "selectall", "selectone", "update", "delete"]:
        print("Error: Las funciones disponibles son: insert, selectone, selectall, update, delete")
        return

    # SUBCUENCAS
    if tableName == "subcuencas":
        if functionName == "insert":
            print(s.insert({
                'nombre': 'Río Turia',
                'codigo': 'SC001',
                'area_km2': 6393,
                'perimetro_km': 280,
                'uso_suelo': 'Urbano',
                'geom': 'POLYGON((720000 4370000, 725000 4370000, 725000 4375000, 720000 4375000, 720000 4370000))'
            }))
        elif functionName == "selectall":
            print(s.selectall())
        elif functionName == "selectone":
            print(s.selectone({'id': 1}))
        elif functionName == "update":
            print(s.update({
                'id': 1,
                'nombre': 'Río Turia',
                'codigo': 'SC001',
                'area_km2': 6393,
                'perimetro_km': 280,
                'uso_suelo': 'Forestal',
                'geom': 'POLYGON((720000 4370000, 725000 4370000, 725000 4375000, 720000 4375000, 720000 4370000))'
            }))
        elif functionName == "delete":
            print(s.delete({'id': 1}))

    # CAUCES
    elif tableName == "cauces":
        if functionName == "insert":
            print(c.insert({
                'nombre': 'Cauce Duplicado',
                'tipo': 'barranco',
                'longitud_km': 10,
                'caudal_medio': 0.5,
                'estado_ecologico': 'Deficiente',
                'geom': 'LINESTRING(727500 4375500, 728000 4376000, 728500 4376500)'
            }))
        elif functionName == "selectall":
            print(c.selectall())
        elif functionName == "selectone":
            print(c.selectone({'id': 1}))
        elif functionName == "update":
            print(c.update({
                'id': 4,
                'nombre': 'Rambla del Poyo',
                'tipo': 'rambla',
                'longitud_km': 38.7,
                'caudal_medio': 1.8,
                'estado_ecologico': 'Deficiente',
                'geom': 'LINESTRING(724500 4373000, 725000 4373500, 725500 4373800)'
            })) #ojo, geometria intersecta
        elif functionName == "delete":
            print(c.delete({'id': 1}))

    # ESTACIONES_MONITOREO
    elif tableName == "estaciones_monitoreo":
        if functionName == "insert":
            print(e.insert({
                'nombre': 'Estación Turia Este',
                'tipo': 'calidad',
                'organismo': 'Ayuntamiento Valencia',
                'estado': 'Mantenimiento',
                'fecha_instalacion': '2020-09-01',
                'geom': 'POINT(724500 4371500)'
            }))
        elif functionName == "selectall":
            print(e.selectall())
        elif functionName == "selectone":
            print(e.selectone({'id': 1}))
        elif functionName == "update":
            print(e.update({
                'id': 5,
                'nombre': 'Estación Turia Este',
                'tipo': 'calidad',
                'organismo': 'Ayuntamiento Valencia',
                'estado': 'En Reparación',
                'fecha_instalacion': '2020-09-01',
                'geom': 'POINT(724500 4371500)'
            }))
        elif functionName == "delete":
            print(e.delete({'id': 1}))

#python manage.py runscript scripts.hidrografiadjango.main --script-args cauces update
#python manage.py runscript scripts.hidrografiadjango.main --script-args subcuencas selectall
#python manage.py runscript scripts.hidrografiadjango.main --script-args estaciones_monitoreo insert
#python manage.py runscript scripts.hidrografiadjango.main --script-args cauces insert
#python manage.py runscript scripts.hidrografiadjango.main --script-args cauces selectall
#python manage.py runscript scripts.hidrografiadjango.main --script-args estaciones_monitoreo insert
#python manage.py runscript scripts.hidrografiadjango.main --script-args estaciones_monitoreo selectalls