print("soy a.py")

from lib2 import b

def printFilename():
    print(__file__)
    print("Invocando a b.py desde a.py")
    b.printFilename()
