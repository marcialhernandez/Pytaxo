#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import sys
import nombres, xmlSalida
import alternativa
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import hashlib

#Funcion que crea una nueva plantilla que corresponde a este tipo de pregunta
#añadiendo los datos obtenidos desde la entrada de
#su mismo tipo, luego una vez completada la pregunta, se imprime
#por pantalla para que la informacion pueda ser recogida por el programa
#principal
def retornaPlantilla(nombreDirectorioPlantillas,xmlEntradaObject,cantidadAlternativas, **kwuargs): #,xmlEntradaObject):
    plantillaSalida=xmlSalida.plantillaGenericaSalida()
    contador=0
    banderaEstado=False
    if 'directorioSalida' in kwuargs.keys():
        banderaEstado=True #Indica si se debe imprimir o no el estado de la cantidad de salidas
    for subRaizSalida in plantillaSalida.iter():
            if subRaizSalida.tag=='plantilla':
                subRaizSalida.set('tipo',xmlEntradaObject.tipo)
                subRaizSalida.set('id',xmlEntradaObject.id)
                subRaizSalida.set('idOrigenEntrada',xmlEntradaObject.idOrigenEntrada)
            if subRaizSalida.tag=='enunciado':
                subRaizSalida.text=xmlEntradaObject.enunciado
            if subRaizSalida.tag=='opciones':
                for conjuntoAlternativas in xmlEntradaObject.agrupamientoAlternativas2(cantidadAlternativas):
                    #Se concatena el texto de todas las alternativas
                    glosasAlternativas=""
                    identificadorPregunta=""
                    for elem in subRaizSalida.getchildren():
                        subRaizSalida.remove(elem)
                    for alternativa in conjuntoAlternativas:
                        opcion = ET.SubElement(subRaizSalida, 'alternativa')
                        opcion.text=alternativa.glosa
                        glosasAlternativas+=alternativa.glosa
                        identificadorPregunta+=alternativa.identificador()
                        opcion.set('puntaje',alternativa.puntaje)
                        opcion.set('id',alternativa.llave)
                        opcion.set('tipo',alternativa.tipo)
                        hijo=ET.SubElement(opcion, 'comentario')
                        hijo.text=alternativa.comentario
                    #A partir del texto concatenado, se crea una unica ID que representa las alternativas
                    #Esta ID se asigna a un nuevo atributo a la subRaiz 'opciones'
                    identificadorItem=hashlib.sha256(glosasAlternativas).hexdigest()
                    subRaizSalida.set('id',identificadorItem)
                    subRaizSalida.set('idPreguntaGenerada',identificadorPregunta.rstrip())
                    contador+=1
                    if banderaEstado==True:
                        xmlSalida.escribePlantilla(kwuargs['directorioSalida'],xmlEntradaObject.tipo, identificadorItem+' '+identificadorPregunta.rstrip()+' '+str(contador), plantillaSalida,'xml')
                    else:
                        print ET.tostring(plantillaSalida, 'utf-8', method="xml")
    if banderaEstado==True:
        print str(contador)+' Creados'                            
    pass

# Declaracion de directorio de entradas
nombreDirectorioEntradas="./Entradas/Definiciones"
nombreDirectorioPlantillas="./Plantillas"
nombreDirectorioSalidas="Salidas"
nombreCompilador="python"
tipoPregunta="enunciadoIncompleto"
listaXmlEntrada=list()

#Ahora la entrada que indica la cantidad de alternativas viene incrustada como atributo en los respectivos
#XML de entrada
#cantidadAlternativas=xmlSalida.argParse()

if nombres.validaExistenciasSubProceso(nombreDirectorioEntradas)==True:
    listaXmlEntrada=xmlSalida.lecturaXmls(nombreDirectorioEntradas, tipoPregunta)

for cadaXmlEntrada in listaXmlEntrada:
    retornaPlantilla(nombreDirectorioPlantillas, cadaXmlEntrada, cadaXmlEntrada.cantidadAlternativas,directorioSalida=nombreDirectorioSalidas+'/'+tipoPregunta)

# # Almacenamiento usando el parser para este tipo de pregunta
# if nombres.validaExistenciasSubProceso(nombreDirectorioEntradas)==True:
#     listaXmlEntrada=lecturaXmls(nombreDirectorioEntradas)
# 
# for cadaXmlEntrada in listaXmlEntrada:
#     retornaPlantilla(cadaXmlEntrada)