import django
import psycopg
import sys
print(django.VERSION)

from lib1 import a

django.VERSION
print(sys.path)

a.printFilename()

def funcion(p1, p2):
    a=25
    return p1 + p2

def funcion2(p1, p2):
    a=30
    funcion(p1, p2)

class Point2D:
    tipo='Topografia'
    def __init__(self, x, y): #Constructor
        #Variables de instancia
        #dispobibles en toda la clase con self.variable
    
        self.setX=x
        self.setY=y
    def printCoordinates(self):
        #Variables locales, solo viven aquí
        a=10
        b=20
        c=a+b
        print(f"({self.x}, {self.y})")

    def translate(self):
        self.y = self
#Setter -- comprueban datos de entrada
    def setX(self,x):
        self.x=self.__checkValue
#Setter
    def setY(self,y):
        self.y = y.__checkValue

#método privado. Empieza por __
    def __checkValue(self, value): # __ eso significa metodo privado, no debes usarlo fuera de la clase
        try: 
            value = float(value)
        except Exception:
            raise Exception('The text is not convertible in to number')
        if value<0:
            raise("Negative values are not allowed")
        return value

pt1 = Point2D(10,10) #Necesito pasarle dos datos, ya que el constructor me pide 2 requerimientos, si paso menos da error
pt1.printCoordinates
#pt1.setX(20)
pt1.printCoordinates

pt1.x=800
print(pt1.tipo)

pt2=Point2D(50,50)
print(pt2.tipo)

Point2D.tipo='Geodesia'
print(pt1.tipo)
print(pt2.tipo)

