#!/usr/bin/env python
# -*- coding: utf-8 -*-
import archivos.acceso as acceso
import archivos.nombres as nombres
from clases import item
import argparse

nombreCarpetaModulo="Modulos"
nombreCarpetaTipos=['v1','v2','v3'] # v4, v5, v6, ....... n
nombreModulosDisponibles=["MC_def_simple","MC_definicionPareada","MC_enunciadoIncompleto","MC_pythonCompara","MC_pythonIterativo","MC_pythonIterativoInvertido","MC_pythonTraza"]
nombreCompilador="python"
nombreTipoAGenerar=""

parser = argparse.ArgumentParser(description='Tipo de pregunta a crear')

parser.add_argument('-v', required=True,choices=nombreCarpetaTipos,
                    help='Especifica el tipo de pregunta a crear: Esta disponible los argumentos "def","exp" y "cod"',
                    metavar="TipoDePregunta")

parser.add_argument('-m', required=False,choices=nombreModulosDisponibles,
                    help='Especifica el tipo de pregunta a crear: Esta disponible los argumentos "def","exp" y "cod"',
                    metavar="TipoDePregunta")

#Analizo que tipo de pregunta quiere generar
if parser.parse_args().v=="v1":
    nombreTipoAGenerar=nombreCarpetaModulo+'/'+nombreCarpetaTipos[0]
elif parser.parse_args().v=="v2":
    nombreTipoAGenerar=nombreCarpetaModulo+'/'+nombreCarpetaTipos[1]
elif parser.parse_args().v=="v3":
    nombreTipoAGenerar=nombreCarpetaModulo+'/'+nombreCarpetaTipos[2]
    
#elif parser.parse_args().t=="v4"
#elif parser.parse_args().t=="v5"
#elif parser.parse_args().t=="v6"
#...
#...
#...
#elif parser.parse_args().t=="n"

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
            acceso.obtenerResultadosModulo(modulo,nombreCompilador).printModuloPregunta()
    else:
        for modulo in listaModulosDisponibles:
            if str(parser.parse_args().m) in modulo:
                modulo=nombreTipoAGenerar+"/"+modulo
                acceso.obtenerResultadosModulo(modulo,nombreCompilador).printModuloPregunta()
                break;