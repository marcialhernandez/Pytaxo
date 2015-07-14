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

import os, sys
sys.path.insert(0, os.getcwd())
from archivos import nombres
import archivos.xmlSalida as xmlSalida
import clases.plantilla as plantilla


try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

#Funcion que analiza la plantilla que corresponde a este tipo de pregunta
#A esa plantilla se le añaden los datos obtenidos desde la entrada de
#su mismo tipo, luego una vez completada la pregunta, se imprime
#por pantalla para que la informacion pueda ser recogida por el programa
#principal

def recogePlantillas(nombreDirectorioPlantillas,tipoPregunta):
    validaPlantilla=False
    taxonomia=""
    plantillasValidas=list()
    for archivoPlantilla in nombres.especificDirectoryNames(nombreDirectorioPlantillas):
        nombreDirectorioArchivoPlantilla=nombres.directorioReal(nombreDirectorioPlantillas+"/"+archivoPlantilla)
        arbolXmlPlantillaEntrada = ET.ElementTree() # instantiate an object of *class* `ElementTree`
        arbolXmlPlantillaEntrada.parse(nombreDirectorioArchivoPlantilla)
        #arbolXml=ET.ElementTree(file=nombreDirectorioArchivoPlantilla)
        for subRaiz in arbolXmlPlantillaEntrada.iter('plantilla'):
            if subRaiz.attrib['tipo']==tipoPregunta:
                validaPlantilla=True
                taxonomia=subRaiz.attrib['taxo']
                     
        if validaPlantilla==True:
            enunciado=""
            for subRaiz in arbolXmlPlantillaEntrada.iter():
                if subRaiz.tag=='glosa':
                    enunciado=enunciado+subRaiz.text
                if subRaiz.tag=='termino':
                    enunciado=enunciado+' @termino'
            #plantillasValidas.append(arbolXmlPlantillaEntrada)
            plantillasValidas.append(plantilla.plantilla(tipoPregunta,enunciado.rstrip(),taxo=taxonomia))
            validaPlantilla=False
    return plantillasValidas
    
def retornaPlantilla(nombreDirectorioPlantillas,xmlEntradaObject,cantidadAlternativas, tipoPregunta, **kwuargs): #,xmlEntradaObject):
    #tipoPregunta=nombres.nombreScript(__file__)
    contador=0
    banderaEstado=False
    if 'directorioSalida' in kwuargs.keys():
        banderaEstado=True #Indica si se debe imprimir o no el estado de la cantidad de salidas
    for plantilla in recogePlantillas(nombreDirectorioPlantillas,tipoPregunta):
        plantillaSalida=xmlSalida.plantillaGenericaSalida()
        for subRaizSalida in plantillaSalida.iter():
                if subRaizSalida.tag=='plantilla':
                    subRaizSalida.set('tipo',xmlEntradaObject.tipo)
                    subRaizSalida.set('id',xmlEntradaObject.id)
                    subRaizSalida.set('idOrigenEntrada',xmlEntradaObject.idOrigenEntrada)
                    subRaizSalida.set('taxonomia',plantilla.taxo)
                if subRaizSalida.tag=='enunciado':
                    subRaizSalida.text=plantilla.enunciado.replace('@termino',xmlEntradaObject.termino)
                if subRaizSalida.tag=='opciones':
                    for conjuntoAlternativas in xmlEntradaObject.agrupamientoAlternativas2(cantidadAlternativas):
                        contador+=1
                        identificadorItem,identificadorAlternativas=xmlSalida.incrustaAlternativasXml(subRaizSalida, conjuntoAlternativas)
                        if banderaEstado==True:
                            xmlSalida.escribePlantilla(kwuargs['directorioSalida'],xmlEntradaObject.tipo,xmlEntradaObject.idOrigenEntrada+"-"+identificadorItem+' '+identificadorAlternativas+' '+str(contador), plantillaSalida,'xml')
                        else:
                            print ET.tostring(plantillaSalida, 'utf-8', method="xml")
    if banderaEstado==True:
        print xmlEntradaObject.idOrigenEntrada+"->"+str(contador)+' Creados'                            
    pass

# Declaracion de directorio de entradas
nombreDirectorioEntradas="./Entradas"
nombreDirectorioPlantillas="./Plantillas"
nombreDirectorioSalidas="Salidas"
nombreCompilador="python"
tipoPregunta='definicion'
listaXmlEntrada=list()

# Almacenamiento usando el parser para este tipo de pregunta

#Ahora la entrada que indica la cantidad de alternativas viene incrustada como atributo en los respectivos
#XML de entrada
#cantidadAlternativas=xmlSalida.argParse()

if nombres.validaExistenciaArchivo(nombreDirectorioEntradas)==True:
    listaXmlEntrada=xmlSalida.lecturaXmls(nombreDirectorioEntradas, tipoPregunta)

for cadaXmlEntrada in listaXmlEntrada:
    retornaPlantilla(nombreDirectorioPlantillas, cadaXmlEntrada, cadaXmlEntrada.cantidadAlternativas,tipoPregunta, directorioSalida=nombreDirectorioSalidas+'/'+tipoPregunta)

#La forma para quitar los signos que no fueron pasados correctamente desde
#la entrada es la siguiente
# enunciadoSinTermino.encode("ascii","ignore")
#         #.translate(dict.fromkeys(map(ord, u",!.;¿?")))