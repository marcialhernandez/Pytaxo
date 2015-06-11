#!/usr/bin/env python
# -*- coding: utf-8 -*-
import inspect, os


def directorioReal(entrada):
    try:
#         filename =  'Entradas/Codigo/testEntrada1.py' # where we were when the module was loaded
        nombreArchivo =  entrada # where we were when the module was loaded
    except NameError: # fallback
        nombreArchivo = inspect.getsourcefile(directorioReal)
    return os.path.realpath(nombreArchivo)+"" 

#Funcion que retorna lista con los nombres de los archivos/carpetas del
#directorio actual
def currentDirectoryNames():
    listaDirectorios=list()
    for dirname, dirnames, filenames in os.walk('.'):
    # print path to all subdirectories first.
        for subdirname in dirnames:
            #listaDirectorios.append(subdirname)
            listaDirectorios.append(os.path.join(dirname, subdirname))
    return listaDirectorios

def currentSubdirectoyNames():
    for dirname, dirnames, filenames in os.walk('.'):
    # print path to all subdirectories first.
    # print path to all filenames.
        for filename in filenames:
            print os.path.join(dirname, filename)
    pass

#Funcion que obtiene los subarchivos del directorio entregado como argumento
def especificDirectoryNames(nombreArchivo):
    listaDirectorios=list()
    for dirname, dirnames, filenames in os.walk(nombreArchivo):
        for filename in filenames:
            if not "__init__" in filename and not ".DS_Store" in filename and not "traceFuntions" in filename and not "testEstandar" in filename:
                listaDirectorios.append(filename)
            #print os.path.join(dirname, filename)
    return listaDirectorios

#Funcion que obtiene las rutas de los subarchivos del directorio entregado como argumento
def fullEspecificDirectoryNames(nombreArchivo):
    listaDirectorios=list()
    for dirname, dirnames, filenames in os.walk(nombreArchivo):
        for filename in filenames:
            listaDirectorios.append(os.path.join(dirname, filename))
            #print os.path.join(dirname, filename)
    return listaDirectorios

def fullEspecificDirectoryNamesXML(nombreArchivo):
    listaDirectorios=list()
    for dirname, dirnames, filenames in os.walk(nombreArchivo):
        for filename in filenames:
            if ".xml" in filename:
                listaDirectorios.append(os.path.join(dirname, filename))
            #print os.path.join(dirname, filename)
    return listaDirectorios

def validaExistenciaArchivo(nombreArchivo):
    listaDirectorios=currentDirectoryNames()
    estado=False
    for nombre in listaDirectorios:
        if nombre==nombreArchivo:
            estado=True
    if estado==False:
        mensaje= "Sistema: No existe el archivo '" +nombreArchivo +"'"
        print (mensaje)
    return estado

#Valida la existencia de la carpeta "Entradas/directorioEspecifico y ademas si este contiene subArchivos"
def validaExistenciasSubProceso(nombreDirectorioEntradas):
    flagExistenciaDirectorioEntrada=0
    flagExistenciaDirectorioEsp=0
    listaArchivosEntrada=list()
    for directorio in nombresSubCarpetas("."):
        if directorio=='./Entradas':
            flagExistenciaDirectorioEntrada=1
    
    if flagExistenciaDirectorioEntrada==0:
        print "Sistema: No existe la carpeta ./Entradas"
        return False
    
    for directorio2 in nombresSubCarpetas("./Entradas"):
        if directorio2==nombreDirectorioEntradas:
            flagExistenciaDirectorioEsp=1
            
    if flagExistenciaDirectorioEsp==0:
        print "Sistema: No existe la carpeta "+nombreDirectorioEntradas
        return False
    
    listaArchivosEntrada=especificDirectoryNames(nombreDirectorioEntradas)
    if len(listaArchivosEntrada)==0:
        print "Sistema: la carpeta "+ nombreDirectorioEntradas + " No contiene entradas para procesar"
        return False
    
    return True

def validaCantidadContenido(nombreCarpeta):
    estado=validaExistenciaArchivo(nombreCarpeta)
    if estado==False:
        return estado
    
    listaDirectorios=especificDirectoryNames(nombreCarpeta)
    if len(listaDirectorios)==0:
        mensaje="La carpeta '" +nombreCarpeta +"'  no contiene modulos para procesar"
        print (mensaje)
        estado=False
    return estado

#Funcion que obtiene nombre de archivo
#Argumento:
#string que representa ruta de archivo, ejemplo: "Modulos/test1.py"
def obtieneNombreArchivo(rutaArchivo):
    nombre=""
    if '/' in rutaArchivo:
        cadena=rutaArchivo.split("/")
        largoCadena=len(cadena)-1
        nombre=cadena[largoCadena]
    else:
        nombre=rutaArchivo
    nombre=nombre.replace(".py","")
    nombre=nombre.replace(".xml","")
    return nombre

def nombresSubCarpetas (directorio):
    return filter(os.path.isdir, [os.path.join(directorio,f) for f in os.listdir(directorio)])

#Funcion que retorna el nombre del script ejecutado
def nombreScript(nombreArchivo):
    nombreArchivo=os.path.basename(nombreArchivo)
    nombreArchivo=nombreArchivo.replace(".py","")
    return nombreArchivo