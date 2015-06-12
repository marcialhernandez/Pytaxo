#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os, sys
sys.path.insert(0, os.getcwd())
import archivos.acceso as acceso
import archivos.nombres as nombres
from clases import item


nombreCarpetaModulo="Modulos"
diccionarioTiposVersusModulos={}
diccionarioTiposVersusModulos["v1"]=["MC_def_simple","MC_definicionPareada","MC_enunciadoIncompleto","MC_pythonCompara","MC_pythonIterativo","MC_pythonIterativoInvertido","MC_pythonTraza"]
nombreCompilador="python"
opcionesModulos=[]
nombreTipoAGenerar=""
for key in diccionarioTiposVersusModulos.keys():
    opcionesModulos.append(key+": "+" ".join(diccionarioTiposVersusModulos[key]))

parser = argparse.ArgumentParser(description='Argumentos de entrada de Pytaxo')

parser.add_argument('-v', required=True,choices=" ".join(diccionarioTiposVersusModulos.keys()),
                    help='Especifica la versión de Pytaxo a ejecutar. Estan disponibles los argumentos: '+" ".join(diccionarioTiposVersusModulos.keys()),
                    metavar="VersiónConjuntoPreguntas")

parser.add_argument('-m', required=False,choices="\n".join(opcionesModulos),
                    help='Especifica el tipo de pregunta a crear. Estan disponible los argumentos'+ "\n"+"\n".join(opcionesModulos),
                    metavar="TipoPregunta")

nombreTipoAGenerar=nombreCarpetaModulo+'/'+parser.parse_args().v

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