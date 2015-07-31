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

import os, sys,argparse
sys.path.insert(0, os.getcwd())
import hashlib
from archivos import nombres, xmlSalida,acceso
from clases import alternativa

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

#Funcion que crea una nueva plantilla que corresponde a este tipo de pregunta
#añadiendo los datos obtenidos desde la entrada de
#su mismo tipo, luego una vez completada la pregunta, se imprime
#por pantalla para que la informacion pueda ser recogida por el programa
#principal
def retornaPlantilla(nombreDirectorioPlantillas,xmlEntradaObject,cantidadAlternativas,raiz,formato,estilo,taxo, **kwuargs): #,xmlEntradaObject):
    plantillaSalida=xmlSalida.plantillaGenericaSalida(xmlEntradaObject.puntaje,xmlEntradaObject.shuffleanswers,xmlEntradaObject.penalty,xmlEntradaObject.answernumbering)
    contador=0
    banderaEstado=False
    nombreArchivo=""
    if 'directorioSalida' in kwuargs.keys():
        banderaEstado=True #Indica si se debe imprimir o no el estado de la cantidad de salidas
    plantillaSalida.set('tipo',xmlEntradaObject.tipo)
    plantillaSalida.set('id',xmlEntradaObject.id)
    plantillaSalida.set('idOrigenEntrada',xmlEntradaObject.idOrigenEntrada)
    for elem in plantillaSalida.iterfind('name/text'):
            nombreArchivo=elem
    for subRaizSalida in plantillaSalida.iter():
        if subRaizSalida.tag=='questiontext':
            for elem in subRaizSalida.iterfind('text'):
                elem.text=xmlEntradaObject.enunciado
    for conjuntoAlternativas in xmlEntradaObject.agrupamientoAlternativas2(cantidadAlternativas):
        #Se concatena el texto de todas las alternativas
        glosasAlternativas=""
        identificadorPregunta=""
        for elem in plantillaSalida.getchildren():
            if elem.tag=='answer':
                plantillaSalida.remove(elem)
        for alternativa in conjuntoAlternativas:
            opcion = ET.SubElement(plantillaSalida, 'answer')
            if (alternativa.tipo=="solucion"):
                opcion.set('fraction',"100")
            else:
                opcion.set('fraction',"0")
            opcionText=ET.SubElement(opcion, 'text')
            opcionText.text=alternativa.glosa
            glosasAlternativas+=alternativa.glosa
            identificadorPregunta+=alternativa.identificador()
            opcion.set('puntaje',alternativa.puntaje)
            opcion.set('id',alternativa.llave)
            opcion.set('tipo',alternativa.tipo)
            feedback=ET.SubElement(opcion, 'feedback')
            feedbackText=ET.SubElement(feedback, 'text')
            feedbackText.text=alternativa.comentario
        #A partir del texto concatenado, se crea una unica ID que representa las alternativas
        #Esta ID se asigna a un nuevo atributo a la subRaiz 'opciones'
        identificadorItem=hashlib.sha256(glosasAlternativas).hexdigest()
        if banderaEstado==True:
            contador+=1
            id= xmlEntradaObject.idOrigenEntrada+"-"+identificadorItem+' '+identificadorPregunta.rstrip()
            nombreArchivo.text=taxo+"-"+id
            if raiz=='quiz':
                quiz = ET.Element('quiz')
                quiz.append(plantillaSalida)
                xmlSalida.escribePlantilla2(kwuargs['directorioSalida'],xmlEntradaObject.tipo,id,quiz,'xml',formato,estilo)
            else:
                xmlSalida.escribePlantilla2(kwuargs['directorioSalida'],xmlEntradaObject.tipo, id, plantillaSalida,'xml',formato,estilo)
        else:
            print ET.tostring(plantillaSalida, 'utf-8', method="xml")
    if banderaEstado==True:
        print xmlEntradaObject.idOrigenEntrada+"->"+str(contador)+' Creados'                            
    pass

#Obtencion de argumentos de entrada
parser = argparse.ArgumentParser(description='Argumentos de entrada de Pytaxo')
raiz,formato,estilo=acceso.parserAtributos(parser)
# Declaracion de directorio de entradas
nombreDirectorioEntradas="./Entradas"
nombreDirectorioPlantillas="./Plantillas"
nombreDirectorioSalidas="Salidas"
nombreCompilador="python"
tipoPregunta="enunciadoIncompleto"
listaXmlEntrada=list()
#Debido a que este modulo no necesita de plantillas
taxo="recordar"

#Ahora la entrada que indica la cantidad de alternativas viene incrustada como atributo en los respectivos
#XML de entrada
#cantidadAlternativas=xmlSalida.argParse()

if nombres.validaExistenciaArchivo(nombreDirectorioEntradas)==True:
    listaXmlEntrada=xmlSalida.lecturaXmls(nombreDirectorioEntradas, tipoPregunta)

for cadaXmlEntrada in listaXmlEntrada:
    retornaPlantilla(nombreDirectorioPlantillas, cadaXmlEntrada, cadaXmlEntrada.cantidadAlternativas,raiz,formato,estilo,taxo,directorioSalida=nombreDirectorioSalidas+'/'+tipoPregunta)