from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from hidrografia_django.models import Cauces, EstacionesMonitoreo, Subcuencas


class Command(BaseCommand):
    help = "Insertar 10 registros demo en cada tabla de hidrografia_django"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Borrar todos los registros existentes antes de insertar',
        )

    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write(self.style.WARNING("Borrando datos existentes..."))
            Cauces.objects.all().delete()
            EstacionesMonitoreo.objects.all().delete()
            Subcuencas.objects.all().delete()

        # Cauces: 
        cauces_data = [
            ("Río Turia",         "principal",  20.5, "bueno"),
            ("Río Júcar",         "principal",  18.3, "bueno"),
            ("Río Mijares",       "secundario", 12.1, "regular"),
            ("Río Segura",        "principal",  15.7, "malo"),
            ("Arroyo del Bosque", "arroyo",      3.4, "bueno"),
            ("Río Magro",         "secundario",  8.9, "regular"),
            ("Río Cabriel",       "principal",  16.2, "bueno"),
            ("Arroyo Verde",      "arroyo",      2.8, "bueno"),
            ("Río Palancia",      "secundario",  6.5, "regular"),
            ("Río Vinalopó",      "principal",  10.4, "malo"),
        ]
        for i, (nombre, tipo, caudal, estado) in enumerate(cauces_data):
            y = 4370000 + i * 500
            geom = GEOSGeometry(
                f"LINESTRING(727000 {y}, 727500 {y})",
                srid=25830
            )
            Cauces.objects.create(
                nombre=nombre,
                tipo=tipo,
                caudal_medio=caudal,
                estado_ecologico=estado,
                geom=geom,
            )
        self.stdout.write(self.style.SUCCESS(f"✓ {len(cauces_data)} cauces insertados"))

        # Estaciones: 
        estaciones_data = [
            ("Estación Manises",   "aforo",   "CHJ"),
            ("Estación Sagunto",   "meteo",   "AEMET"),
            ("Estación Valencia",  "calidad", "Generalitat"),
            ("Estación Cullera",   "aforo",   "CHJ"),
            ("Estación Gandía",    "meteo",   "AEMET"),
            ("Estación Xàtiva",    "calidad", "Generalitat"),
            ("Estación Requena",   "aforo",   "CHJ"),
            ("Estación Utiel",     "meteo",   "AEMET"),
            ("Estación Buñol",     "calidad", "Generalitat"),
            ("Estación Carlet",    "aforo",   "CHJ"),
        ]
        estados = ["activa", "activa", "mantenimiento",
                   "activa", "inactiva", "activa",
                   "activa", "activa", "mantenimiento", "activa"]
        for i, ((nombre, tipo, org), estado) in enumerate(zip(estaciones_data, estados)):
            x = 728000 + i * 200
            y = 4371000
            geom = GEOSGeometry(f"POINT({x} {y})", srid=25830)
            EstacionesMonitoreo.objects.create(
                nombre=nombre,
                tipo=tipo,
                organismo=org,
                estado=estado,
                fecha_instalacion=f"2020-{(i % 12) + 1:02d}-15",
                geom=geom,
            )
        self.stdout.write(self.style.SUCCESS(f"✓ {len(estaciones_data)} estaciones insertadas"))

        # Subcuencas: 
        subcuencas_data = [
            ("Cuenca Alta del Turia",   "SC001", "forestal"),
            ("Cuenca Media del Turia",  "SC002", "agrícola"),
            ("Cuenca Baja del Turia",   "SC003", "urbano"),
            ("Cuenca del Júcar Norte",  "SC004", "forestal"),
            ("Cuenca del Júcar Sur",    "SC005", "agrícola"),
            ("Cuenca del Mijares",      "SC006", "forestal"),
            ("Cuenca del Palancia",     "SC007", "urbano"),
            ("Cuenca del Magro",        "SC008", "agrícola"),
            ("Cuenca del Cabriel",      "SC009", "forestal"),
            ("Cuenca del Vinalopó",     "SC010", "urbano"),
        ]
        for i, (nombre, codigo, uso) in enumerate(subcuencas_data):
            col = i % 5
            row = i // 5
            x0 = 730000 + col * 300
            y0 = 4370000 + row * 300
            x1, y1 = x0 + 200, y0 + 200
            geom = GEOSGeometry(
                f"POLYGON(({x0} {y0}, {x1} {y0}, {x1} {y1}, {x0} {y1}, {x0} {y0}))",
                srid=25830
            )
            Subcuencas.objects.create(
                nombre=nombre,
                codigo=codigo,
                uso_suelo=uso,
                geom=geom,
            )
        self.stdout.write(self.style.SUCCESS(f"✓ {len(subcuencas_data)} subcuencas insertadas"))

        self.stdout.write(self.style.SUCCESS("\n✓ Datos demo cargados correctamente (30 registros)"))
