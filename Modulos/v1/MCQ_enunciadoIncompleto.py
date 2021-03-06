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

def remueveCaracterNoPermitido(stringEntrada):
    caracteresNoPermitidos=["*","|","\\",":",'"',"<",">","?","/"]
    listaEntrada=list(stringEntrada)
    for caracter in listaEntrada:
        if caracter in caracteresNoPermitidos:
            del caracter
    return "".join(listaEntrada)

#Funcion que crea una nueva plantilla que corresponde a este tipo de pregunta
#añadiendo los datos obtenidos desde la entrada de
#su mismo tipo, luego una vez completada la pregunta, se imprime
#por pantalla para que la informacion pueda ser recogida por el programa
#principal
def retornaPlantilla(nombreDirectorioPlantillas,xmlEntradaObject,cantidadAlternativas,raiz,formato,estilo,taxo,tipoPregunta, **kwuargs): #,xmlEntradaObject):
    plantillaSalida=xmlSalida.plantillaGenericaSalida(xmlEntradaObject.puntaje,xmlEntradaObject.shuffleanswers,xmlEntradaObject.penalty,xmlEntradaObject.answernumbering)
    contador=0
    banderaEstado=False
    nombreArchivo=""
    enunciado=""
    if 'directorioSalida' in kwuargs.keys():
        banderaEstado=True #Indica si se debe imprimir o no el estado de la cantidad de salidas
    plantillaSalida.set('tipo',xmlEntradaObject.tipo)
    plantillaSalida.set('id',xmlEntradaObject.id)
    plantillaSalida.set('idOrigenEntrada',xmlEntradaObject.idOrigenEntrada)
    for parteEnunciado in xmlEntradaObject.enunciado:
        if parteEnunciado["tipo"]=="text":
            enunciado+='<body style="font-family:Tahoma, Geneva, sans-serif;font-size:length" >'+parteEnunciado["text"]+'</body><BR>'
        else:
            enunciado+='<pre id="python" class="prettyprint linenums">'+parteEnunciado["text"]+'</pre>'
    for elem in plantillaSalida.iterfind('name/text'):
            nombreArchivo=elem
    for subRaizSalida in plantillaSalida.iter():
        if subRaizSalida.tag=='questiontext':
            for elem in subRaizSalida.iterfind('text'):
                #elem.text=xmlEntradaObject.enunciado
                
                elem.append(ET.Comment((' --><![CDATA[' + ('<script src="https://google-code-prettify.googlecode.com/svn/loader/run_prettify.js?skin=sons-of-obsidian"></script>'+enunciado).replace(']]>', ']]]]><![CDATA[>')) + ']]><!-- '))

    for conjuntoAlternativas in xmlEntradaObject.agrupamientoEnunciadoIncompleto(cantidadAlternativas,xmlEntradaObject.caracterSeparador,xmlEntradaObject.caracterResaltador):
        pass
        #Se concatena el texto de todas las alternativas
        glosasAlternativas=[]
        identificadorPregunta=[]
        #Se eliminan las alternativas anteriores
        for elem in plantillaSalida.getchildren():
            if elem.tag=='answer':
                plantillaSalida.remove(elem)
        for alternativa in conjuntoAlternativas:
            opcion = ET.SubElement(plantillaSalida, 'answer')
            opcion.set('fraction',str(alternativa.puntaje))
            opcionText=ET.SubElement(opcion, 'text')
            opcionText.append(ET.Comment((' --><![CDATA[' + ('<pre><code class="inline">'+alternativa.glosa+"</code></pre>").replace(']]>', ']]]]><![CDATA[>')) + ']]><!-- '))
            #opcionText.text=alternativa.glosa
            glosasAlternativas.append(alternativa.glosa)
            identificadorPregunta.append(alternativa.llave)
            feedback=ET.SubElement(opcion, 'feedback')
            feedbackText=ET.SubElement(feedback, 'text')
            if alternativa.tipo=="solucion":
                opcion.set('puntaje',str(xmlEntradaObject.puntaje))
            else:
                feedbackText.text=alternativa.comentario
                opcion.set('puntaje',"0")
            opcion.set('id',alternativa.llave)
            opcion.set('tipo',alternativa.tipo)
        #A partir del texto concatenado, se crea una unica ID que representa las alternativas
        #Esta ID se asigna a un nuevo atributo a la subRaiz 'opciones'
        identificadorItem=hashlib.sha256("".join(glosasAlternativas)).hexdigest()
        if banderaEstado==True:
            contador+=1
            #tipoPregunta+"_"+plantillaObject.taxo+"_"+plantillaObject.id+"_"+self.idOrigenEntrada+"_"+identificadorAlternativas
            id =tipoPregunta+"_"+taxo+"_"+xmlEntradaObject.idOrigenEntrada+"_"+"+".join(identificadorPregunta)
            #id= xmlEntradaObject.idOrigenEntrada+"-"+identificadorItem+' '+"|".join(identificadorPregunta)
            nombreArchivo.text=id
            if raiz=='quiz':
                quiz = ET.Element('quiz')
                quiz.append(plantillaSalida)
                xmlSalida.escribePlantilla2(kwuargs['directorioSalida'],xmlEntradaObject.tipo,id,quiz,'xml',formato,estilo,merge=raiz)
            else:
                xmlSalida.escribePlantilla2(kwuargs['directorioSalida'],xmlEntradaObject.tipo, id, plantillaSalida,'xml',formato,estilo,merge=raiz)
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

if raiz=='merge':
    xmlSalida.mergeOperation(nombreDirectorioSalidas+'/'+tipoPregunta,tipoPregunta,'xml','open',formato,estilo)

if nombres.validaExistenciaArchivo(nombreDirectorioEntradas)==True:
    listaXmlEntrada=xmlSalida.lecturaXmls(nombreDirectorioEntradas, tipoPregunta)

for cadaXmlEntrada in listaXmlEntrada:
    retornaPlantilla(nombreDirectorioPlantillas, cadaXmlEntrada, cadaXmlEntrada.cantidadAlternativas,raiz,formato,estilo,taxo,tipoPregunta,directorioSalida=nombreDirectorioSalidas+'/'+tipoPregunta)

if raiz=='merge':
    xmlSalida.mergeOperation(nombreDirectorioSalidas+'/'+tipoPregunta,tipoPregunta,'xml','close',formato,estilo)