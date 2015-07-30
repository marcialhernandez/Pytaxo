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

import argparse
import os, sys
sys.path.insert(0, os.getcwd())
import archivos.acceso as acceso
import archivos.nombres as nombres
from clases import item

nombreCarpetaModulo="Modulos"
diccionarioTiposVersusModulos={}
for versionModulo in nombres.nombresSubCarpetas(nombreCarpetaModulo):
    versionModuloActual=versionModulo.split("/")[-1]
    diccionarioTiposVersusModulos[versionModuloActual]=[]
    for modulo in nombres.especificDirectoryNames(versionModulo):
        diccionarioTiposVersusModulos[versionModuloActual].append(modulo.split(".py")[0])

nombreCompilador="python"
opcionesModulos=[]
nombreTipoAGenerar=""
for key in diccionarioTiposVersusModulos.keys():
    opcionesModulos.append(key+": "+" ".join(diccionarioTiposVersusModulos[key]))

parser = argparse.ArgumentParser(description='Argumentos de entrada de Pytaxo')

parser.add_argument('-v', required=True,choices=" ".join(diccionarioTiposVersusModulos.keys()),
                    help='Especifica la versión de Pytaxo a ejecutar. Estan disponibles los argumentos: '+" ".join(diccionarioTiposVersusModulos.keys()),
                    metavar="VersiónConjuntoPreguntas")

parser.add_argument('-m', required=False,
                    help='Especifica el tipo de pregunta a crear. Estan disponible los argumentos'+ "\n"+"\n".join(opcionesModulos),
                    metavar="TipoPregunta")

raiz,formato,estilo=acceso.parserAtributos(parser)
raiz="-r "+raiz
formato="-f "+formato
estilo="-s "+estilo
# parser.add_argument('-r', required=False,
#                     help='Especifica la raiz de las preguntas a generar. Puede ser "answer" o "quiz"',
#                     metavar="RaizPregunta")
# 
# parser.add_argument('-f', required=False,
#                     help='Especifica si es necesaria agregar la primera linea que especifica el formato',
#                     metavar="FormatoPregunta")
# 
# parser.add_argument('-s', required=False,
#                     help='Especifica si hay o no un archivo de estilo adjunto',
#                     metavar="EstiloPregunta")

if parser.parse_args().m!=None and (not str(parser.parse_args().m).rstrip().lstrip() in diccionarioTiposVersusModulos[parser.parse_args().v]):
    print ("No existe el modulo: '"+parser.parse_args().m+"'" )
    exit()

# raiz=str(parser.parse_args().r).lower()
# if raiz in ['answer','quiz']:
#     pass
# else:
#     raiz='quiz'
# 
# formato=str(parser.parse_args().f).lower()
# if formato in ['si','no']:
#     pass
# else:
#     formato='si'
# 
# estilo=str(parser.parse_args().s).lower()
# if estilo in ['si','no']:
#     if estilo=='si':
#         estilo='default'
# else:
#     estilo='default'

nombreTipoAGenerar=nombreCarpetaModulo+'/'+str(parser.parse_args().v).rstrip().lstrip()

banderaModuloEspecifico=False
    
listaModulosDisponibles=list()
flagInexistenciaModuloIndicado=1
for tipoPreguntaDisponible in nombres.nombresSubCarpetas(nombreCarpetaModulo):
    if tipoPreguntaDisponible==nombreTipoAGenerar:
        #Implica que la carpeta Modulos existe y que ademas contiene modulos para procesar
        if nombres.validaCantidadContenido('./'+nombreTipoAGenerar)==True:
            listaModulosDisponibles=nombres.especificDirectoryNames(nombreTipoAGenerar)
            flagInexistenciaModuloIndicado=0

if flagInexistenciaModuloIndicado==1: 
    moduloInexistente=nombreTipoAGenerar.split("/")[1]
    print "No existe el modulo "+moduloInexistente +" para generar las preguntas pedidas"

else:
    print nombreTipoAGenerar
    if parser.parse_args().m==None:
        for modulo in listaModulosDisponibles:
            modulo=nombreTipoAGenerar+"/"+modulo
            acceso.obtenerResultadosModulo(modulo,nombreCompilador,raiz,formato,estilo).printModuloPregunta()
    else:
        for modulo in listaModulosDisponibles:
            if str(parser.parse_args().m) in modulo:
                modulo=nombreTipoAGenerar+"/"+modulo
                acceso.obtenerResultadosModulo(modulo,nombreCompilador,raiz,formato,estilo).printModuloPregunta()
                break;