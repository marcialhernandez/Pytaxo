#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess, stat, os, tempfile

import item, entrada
from nombres import obtieneNombreArchivo


#Funcion que otorga permisos de acceso a un archivo
#Argumentos:
#-Ruta de archivo y su nombre por ejemplo "Modulos/test1.py"
def permisoAcceso(rutaArchivo):
    st = os.stat(rutaArchivo)
    os.chmod(rutaArchivo, st.st_mode | stat.S_IEXEC)

def formateaResultado(resultado):
    resultado=resultado.split("\n")
    while "" in resultado:
        resultado.remove("")
         
    return resultado
    
#Funcion que ejecuta un modulo creado y obtiene sus resultados
#Argumentos:
#-Ruta de archivo y su nombre por ejemplo "Modulos/test1.py"
#-lenguaje compilador del modulo, por ejemplo "python"
def obtenerResultadosModulo(rutaArchivo, lenguaje):
    permisoAcceso(rutaArchivo)
    proceso = subprocess.Popen([lenguaje, rutaArchivo],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output, errors = proceso.communicate()
    if proceso.returncode:
        try:
            raise Exception(errors)
        except Exception as falla:
            #print type(falla.args)
            #print type(falla.args[0])
            return item.item(obtieneNombreArchivo(rutaArchivo),"",formateaResultado(falla.args[0]))
    else:
        #print output
        return item.item(obtieneNombreArchivo(rutaArchivo),formateaResultado(output),"")

#Funcion que ejecuta una entrada y obtiene sus resultados
#Argumentos:
#-Ruta de archivo y su nombre por ejemplo "Modulos/test1.py"
#-lenguaje compilador del modulo, por ejemplo "python"
def obtenerResultadosEntrada(rutaArchivo, lenguaje):
    permisoAcceso(rutaArchivo)
    proceso = subprocess.Popen([lenguaje, rutaArchivo],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output, errors = proceso.communicate()
    if proceso.returncode:
        try:
            raise Exception(errors)
        except Exception as falla:
            #print type(falla.args)
            #print type(falla.args[0])
            return entrada.entrada(obtieneNombreArchivo(rutaArchivo),"",formateaResultado(falla.args[0]))
    else:
        #print output
        return entrada.entrada(obtieneNombreArchivo(rutaArchivo),formateaResultado(output),"")

def CrearDirectorio(rutaNuevoDirectorio):
    try:
        os.makedirs(rutaNuevoDirectorio)
    except OSError:
        if os.path.exists(rutaNuevoDirectorio):
            pass
        # We are nearly safe
        else:
        # There was an error on creation, so make sure we know about it
            raise

def make_tempfile(datos):
    fd = tempfile.NamedTemporaryFile(mode='w+b',suffix='.py', delete=False)
    try:
        #fd.write("import pdb\n\n") #debug module
        #fd.write("pdb.set_trace()")
        fd.write(datos)
        fd.seek(0)
    finally:
        fd.close()
    return fd

def cleanup(filename):
    os.unlink(filename)