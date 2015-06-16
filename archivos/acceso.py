#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)

Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use. 

NonCommercial — You may not use the material for commercial purposes.

NoDerivatives — If you remix, transform, or build upon the material, you may not distribute the modified material. 

No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits. 

https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode#languages

Copyright (C)
@author: Marcial Hernandez Sanchez
@date: 16/6/2015
University of Santiago, Chile (Usach)"""

import subprocess, stat, os, tempfile
import clases.entrada as entrada
import clases.item as item
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

def make_traceFuntionsFile(datos):
    fd = tempfile.NamedTemporaryFile(mode='w+b',suffix='.py', delete=False)
    try:
        #fd.write("import pdb\n\n") #debug module
        #fd.write("pdb.set_trace()")
        fd.write(datos)
        fd.seek(0)
    finally:
        fd.close()
    return fd
    pass

def make_tempPython(datos, funcionTracer,testEstandar):
    fd = tempfile.NamedTemporaryFile(mode='w+b',suffix='.py', delete=False)
    try:
        fd.write(funcionTracer)
        fd.write("\n\n")
        fd.write(datos)
        fd.write("\n\n")
        fd.write(testEstandar)
        fd.write("\n\n")
        #No me combiene dejar el puntero al principio, pues seguire agregando informacion en un futuro
        #fd.seek(0)
    finally:
        fd.close()
    return fd

def make_tempPython2(datos, funcionTracer,testEstandar,funcionEntrada):
    
    fd = tempfile.NamedTemporaryFile(mode='w+b',suffix='.py', delete=False)
    try:
        fd.write(funcionTracer)
        fd.write("\n\n")
        fd.write(datos)
        fd.write("\n\n")
        for linea in testEstandar:
            if "funcion(x)" in linea:
                linea='    '+funcionEntrada+'\n'
                fd.write(linea)
            else:
                fd.write(linea)
        #testEstandar.replace("x=funcion(x)","x="+funcionEntrada)
        #print "bbbbbb    "+testEstandar
        #fd.write(testEstandar)
        fd.write("\n\n")
        #No me combiene dejar el puntero al principio, pues seguire agregando informacion en un futuro
        #fd.seek(0)
    finally:
        fd.close()
    return fd

def cleanup(filename):
    os.unlink(filename)