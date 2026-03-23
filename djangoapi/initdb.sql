create extension postgis;
create schema d;

CREATE TABLE d.subcuencas(
id SERIAL PRIMARY KEY,
nombre TEXT,
codigo VARCHAR(10),
area_km2 DOUBLE PRECISION,
perimetro_km DOUBLE PRECISION,
uso_suelo VARCHAR(20),
geom GEOMETRY(POLYGON, 25830)
);

CREATE TABLE d.cauces(
id SERIAL PRIMARY KEY,
nombre TEXT,
tipo VARCHAR(20),
longitud_km DOUBLE PRECISION,
caudal_medio DOUBLE PRECISION,
estado_ecologico VARCHAR(100),
geom GEOMETRY(LINESTRING, 25830)
);

CREATE TABLE d.estaciones_monitoreo(
id SERIAL PRIMARY KEY,
nombre TEXT,
tipo VARCHAR(20),
organismo VARCHAR(50),
estado VARCHAR(100),
fecha_instalacion DATE,
geom GEOMETRY(POINT, 25830)
);

