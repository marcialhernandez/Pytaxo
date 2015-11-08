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

import argparse,re
import subprocess, stat, os, tempfile
import clases.entrada as entrada
import clases.item as item
from nombres import obtieneNombreArchivo
from itertools import product,chain,combinations

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def powerSetAll(iterable):
    lista=list(powerset(iterable))
    del lista[0]
    listaResultado=[]
    for elemento in lista:
        listaResultado.append(list(elemento))
    return listaResultado

def remplazoCombinatorial(stringEntrada, from_char, to_char):
    options = [(fragmentoStringEntrada,) if fragmentoStringEntrada != from_char else (from_char, to_char) for fragmentoStringEntrada in re.split("("+from_char+")", stringEntrada)]
    return (list(''.join(o) for o in product(*options)))

#{x:y}
def remplazoCombinatorialDict(stringEntrada, dictObject):
    options = [(fragmentoStringEntrada,) if fragmentoStringEntrada not in dictObject.keys() else (fragmentoStringEntrada, dictObject[fragmentoStringEntrada]) for fragmentoStringEntrada in re.split("("+'|'.join(dictObject.keys())+")", stringEntrada)]
    return (list(''.join(o) for o in product(*options)))

def union(a, b):
    """ return the union of two lists """
    return list(set(a) | set(b))
    
def generaCondicion(turnoCondicion):
    if turnoCondicion==0:
        return {"!=":"==","==":"!="}
    else:
        return {"<":">",">":"<"}

def generaCondiciones(stringEntrada):
    listaTotalCondiciones=[]
    listaCondiciones0=remplazoCombinatorialDict(stringEntrada,generaCondicion(0))
    listaCondiciones1=remplazoCombinatorialDict(stringEntrada,generaCondicion(1))
    
    for condicion in listaCondiciones0:
        listaTotalCondiciones=union(listaTotalCondiciones,remplazoCombinatorialDict(condicion,generaCondicion(1)))
        
    for condicion in listaCondiciones1:
        listaTotalCondiciones=union(listaTotalCondiciones,remplazoCombinatorialDict(condicion,generaCondicion(0)))
    
    listaCondicionesPreliminares=union(listaCondiciones0,listaCondiciones1)
    
    listaTotalCondiciones=union(listaTotalCondiciones,listaCondicionesPreliminares)
    #print listaTotalCondiciones
    return listaTotalCondiciones

def parserAtributos(parser):
    parser.add_argument('-r', required=False,
                    help='Especifica la raiz de las preguntas a generar. Puede ser "answer", "quiz" o "merge"',
                    metavar="RaizPregunta")
    
    parser.add_argument('-f', required=False,
                        help='Especifica si es necesaria agregar la primera linea que especifica el formato',
                        metavar="FormatoPregunta")
    
    parser.add_argument('-s', required=False,
                        help='Especifica si hay o no un archivo de estilo adjunto',
                        metavar="EstiloPregunta")
    
    raiz=str(parser.parse_args().r).lower().rstrip().lstrip()
    if raiz in ['answer','quiz','merge']:
        pass
    else:
        raiz='quiz'
    
    formato=str(parser.parse_args().f).lower().rstrip().lstrip()
    if formato in ['si','no']:
        pass
    else:
        formato='si'
    
    estilo=str(parser.parse_args().s).lower().rstrip().lstrip()
    if estilo in ['si','no']:
        if estilo=='si':
            estilo='default'
    else:
        if estilo=="none":
            estilo='default'
    return raiz,formato,estilo

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
def obtenerResultadosModulo(rutaArchivo, lenguaje,raiz,formato,estilo):
    permisoAcceso(rutaArchivo)
    proceso = subprocess.Popen([lenguaje, rutaArchivo,raiz,formato,estilo],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output, errors = proceso.communicate()
    if proceso.returncode:
        try:
            raise Exception(errors)
        except Exception as falla:
            return item.item(obtieneNombreArchivo(rutaArchivo),"",formateaResultado(falla.args[0]))
    else:
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
            return entrada.entrada(obtieneNombreArchivo(rutaArchivo),"",formateaResultado(falla.args[0]))
    else:
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
        fd.write(datos)
        fd.seek(0)
    finally:
        fd.close()
    return fd
    pass

def make_tempPython(datos, funcionTracer,testEstandar):
    fd = tempfile.NamedTemporaryFile(mode='w+b',suffix='.py', delete=False)
    try:
        fd.write("#!/usr/bin/env python"+"\n"+"# -*- coding: utf-8 -*-"+"\n")
        fd.write("import sys"+"\n"+"reload(sys)"+"\n"+"sys.setdefaultencoding('utf8')"+"\n")
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
        fd.write("#!/usr/bin/env python"+"\n"+"# -*- coding: utf-8 -*-"+"\n")
        fd.write("import sys"+"\n"+"reload(sys)"+"\n"+"sys.setdefaultencoding('utf8')"+"\n")
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
        fd.write("\n\n")
        #No me combiene dejar el puntero al principio, pues seguire agregando informacion en un futuro
        #fd.seek(0)
    finally:
        fd.close()
    return fd

def make_tempPython2(datos, funcionTracer,testEstandar,funcionEntrada):
    
    fd = tempfile.NamedTemporaryFile(mode='w+b',suffix='.py', delete=False)
    try:
        fd.write("#!/usr/bin/env python"+"\n"+"# -*- coding: utf-8 -*-"+"\n")
        fd.write("import sys"+"\n"+"reload(sys)"+"\n"+"sys.setdefaultencoding('utf8')"+"\n")
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
        fd.write("\n\n")
        #No me combiene dejar el puntero al principio, pues seguire agregando informacion en un futuro
        #fd.seek(0)
    finally:
        fd.close()
    return fd

def make_tempPython3(datos, funcionTracer,testEstandar,funcionEntrada,condicion,nuevaCondicion):
    fd = tempfile.NamedTemporaryFile(mode='w+b',suffix='.py', delete=False)
    try:
        datos2=""
        fd.write("#!/usr/bin/env python"+"\n"+"# -*- coding: utf-8 -*-"+"\n")
        fd.write("import sys"+"\n"+"reload(sys)"+"\n"+"sys.setdefaultencoding('utf8')"+"\n")
        fd.write(funcionTracer)
        fd.write("\n\n")
        for posicionCondicion in range(len(condicion)):
            #print condicion[posicionCondicion]+" switch "+nuevaCondicion[posicionCondicion]
            datos2=datos.replace(condicion[posicionCondicion],nuevaCondicion[posicionCondicion])
        fd.write(datos2)
        fd.write("\n\n")
        for linea in testEstandar:
            if "funcion(x)" in linea:
                linea='    '+funcionEntrada+'\n'
                fd.write(linea)
            else:
                fd.write(linea)
        fd.write("\n\n")
        #print (funcionEntrada)
        #No me combiene dejar el puntero al principio, pues seguire agregando informacion en un futuro
        #fd.seek(0)
    finally:
        fd.close()
    return fd

def make_tempPythonConcidicionado(datos, funcionTracer,testEstandar,funcionEntrada,condicion):
    #Genero todas las agrupaciones de diferentes condiciones
    #Si las condiciones son [A,B] queda [[A],[B].[A,B]]
    combinacionDeCondiciones=powerSetAll(condicion)
    
    #{condicion:[reemplazos disponibles]}
    #listaCondiciones=[]
    
    #Para cada grupo de condiciones
    #for cadaCombinacionCondiciones in combinacionDeCondiciones:
        
    #Creo un diccionario de condiciones
    diccionarioCondiciones={}
    diccionarioGruposCombinados={}
    #Cada condicion tendra asociada diferentes combinaciones 
    for cadaCondicion in condicion:
        #variaciones logicas
        diccionarioCondiciones[cadaCondicion]=generaCondiciones(cadaCondicion)
    variantesLogicos=list(product(*diccionarioCondiciones.values()))
    #print variantesLogicos
    
    #En variantesLogicos se guardan todas las combinaciones
    #De todas las variantes logicas de las condiciones de entrada
    #Del mismo tamaño que la condicion inicial
    archivosTemporales=[]
    
    for cadaGrupoCondicion in variantesLogicos:
        archivosTemporales.append({"condicion":cadaGrupoCondicion,"archivo":make_tempPython3(datos, funcionTracer,testEstandar,funcionEntrada,condicion,cadaGrupoCondicion)})
    
    #print archivosTemporales
    return archivosTemporales


def cleanup(filename):
    os.unlink(filename)