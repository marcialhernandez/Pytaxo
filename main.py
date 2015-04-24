#!/usr/bin/env python
# -*- coding: utf-8 -*-
import archivos.acceso as acceso
import archivos.nombres as nombres
#from archivos import nombres, acceso
from clases import item
import argparse

nombreCarpetaModulo="Modulos"
nombreCarpetaTipos=['Definiciones','Expresiones','Codigo']
nombreCompilador="python"
nombreTipoAGenerar=""

parser = argparse.ArgumentParser(description='Tipo de pregunta a crear')

parser.add_argument('-t', required=True,choices=['def', 'exp', 'cod'],
                    help='Especifica el tipo de pregunta a crear: Esta disponible los argumentos "def","exp" y "cod"',
                    metavar="TipoDePregunta")

#Analizo que tipo de pregunta quiere generar
if parser.parse_args().t=="def":
    nombreTipoAGenerar=nombreCarpetaModulo+'/'+nombreCarpetaTipos[0]
elif parser.parse_args().t=="exp":
    nombreTipoAGenerar=nombreCarpetaModulo+'/'+nombreCarpetaTipos[1]
else:
    nombreTipoAGenerar=nombreCarpetaModulo+'/'+nombreCarpetaTipos[2]

#nombreTipoAGenerar=nombreCarpetaModulo+'/'+nombreCarpetaTipos[0]
print nombreTipoAGenerar
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
    for modulo in listaModulosDisponibles:
        modulo=nombreTipoAGenerar+"/"+modulo
        acceso.obtenerResultadosModulo(modulo,nombreCompilador).printModuloPregunta()

#acceso.obtenerResultadosModulo("Modulos/test1.py","python").printModuloPregunta()
#acceso.obtenerResultadosModulo("Modulos/test1.py","python")

#print nombres.validaExistenciaArchivo("Modulos")

#print nombres.currentDirectoryNames()
#nombres.especificDirectoryNames("Modulos")