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
from archivos import nombres,acceso
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
    id=""
    plantillasValidas=list()
    for archivoPlantilla in nombres.especificDirectoryNames(nombreDirectorioPlantillas):
        nombreDirectorioArchivoPlantilla=nombres.directorioReal(nombreDirectorioPlantillas+"/"+archivoPlantilla)
        arbolXmlPlantillaEntrada = ET.ElementTree() # instantiate an object of *class* `ElementTree`
        arbolXmlPlantillaEntrada.parse(nombreDirectorioArchivoPlantilla)
        for subRaiz in arbolXmlPlantillaEntrada.iter('plantilla'):
            if subRaiz.attrib['tipo']==tipoPregunta:
                validaPlantilla=True
                try:
                    taxonomia=subRaiz.attrib['taxo']
                except:
                    taxonomia="sinTaxonomia"
                try:
                    id=subRaiz.attrib['id']
                except:
                    id="sinID"
                    
        if validaPlantilla==True:
            enunciado=""
            for subRaiz in arbolXmlPlantillaEntrada.iter():
                if subRaiz.tag=='glosa':
                    enunciado=enunciado+subRaiz.text.rstrip().lstrip()
                #if subRaiz.tag=='termino':
                #    enunciado=enunciado+' @termino'
            plantillasValidas.append(plantilla.plantilla(tipoPregunta,enunciado.rstrip(),id,taxo=taxonomia))
            validaPlantilla=False
    return plantillasValidas
    
def retornaPlantilla(nombreDirectorioPlantillas,xmlEntradaObject,cantidadAlternativas, tipoPregunta,raiz,formato,estilo, **kwuargs): #,xmlEntradaObject):
    contador=0
    banderaEstado=False
    nombreArchivo=""
    archivoSalida=""
    if 'directorioSalida' in kwuargs.keys():
        banderaEstado=True #Indica si se debe imprimir o no el estado de la cantidad de salidas
    for plantilla in recogePlantillas(nombreDirectorioPlantillas,tipoPregunta):
        if xmlEntradaObject.linkPlantilla(plantilla)==False:
            continue
        plantillaSalida=xmlSalida.plantillaGenericaSalida(xmlEntradaObject.puntaje,xmlEntradaObject.shuffleanswers,xmlEntradaObject.penalty,xmlEntradaObject.answernumbering)
        plantillaSalida.set('tipo',xmlEntradaObject.tipo)
        plantillaSalida.set('idOrigenEntrada',xmlEntradaObject.idOrigenEntrada)
        plantillaSalida.set('taxonomia',plantilla.taxo)
        for elem in plantillaSalida.iterfind('name/text'):
            nombreArchivo=elem
        for subRaizSalida in plantillaSalida.iter():
                if subRaizSalida.tag=='questiontext':
                    for elem in subRaizSalida.iterfind('text'):
                        banderaCodigo=False
                        if '@codigo' in plantilla.enunciado:
                            banderaCodigo=True
                            plantilla.enunciado=plantilla.enunciado.split('@codigo')
                            plantilla.enunciado='<pre style="font-family:Tahoma, Geneva, sans-serif;font-size:length" >'+plantilla.enunciado[0]+'</pre><BR><pre id="python" class="prettyprint linenums">'+xmlEntradaObject.codigo+'</pre><BR><p style="font-family:Tahoma, Geneva, sans-serif;font-size:length"><pre style="font-family:Tahoma, Geneva, sans-serif;font-size:length" >'+plantilla.enunciado[1]+'</pre>'
                        if '@termino' in plantilla.enunciado:
                            if banderaCodigo==True:
                                plantilla.enunciado=plantilla.enunciado.replace('@termino',xmlEntradaObject.termino)
                            else:
                                plantilla.enunciado='<pre style="font-family:Tahoma, Geneva, sans-serif;font-size:length" >'+plantilla.enunciado.replace('@termino',xmlEntradaObject.termino)+'</pre>'
                    elem.append(ET.Comment((' --><![CDATA[' + ('<script src="https://google-code-prettify.googlecode.com/svn/loader/run_prettify.js?skin=sons-of-obsidian"></script>'+plantilla.enunciado).replace(']]>', ']]]]><![CDATA[>')) + ']]><!-- '))
                        
        for conjuntoAlternativas in xmlEntradaObject.agrupamientoAlternativas2(cantidadAlternativas):
            contador+=1
            identificadorItem,identificadorAlternativas=xmlSalida.incrustaAlternativasXml(plantillaSalida, conjuntoAlternativas)
            if banderaEstado==True:
                idItem= xmlEntradaObject.idItem(plantilla,tipoPregunta,identificadorAlternativas)
                #idItem=xmlEntradaObject.idOrigenEntrada+"-"+identificadorItem+' '+identificadorAlternativas
                #nombreArchivo.text=plantilla.taxo+"-"+idItem
                nombreArchivo.text=idItem
                if raiz=='quiz':
                    quiz = ET.Element('quiz')
                    quiz.append(plantillaSalida)
                    xmlSalida.escribePlantilla2(kwuargs['directorioSalida'],xmlEntradaObject.tipo,idItem,quiz,'xml',formato,estilo,merge=raiz)
                else:
                    xmlSalida.escribePlantilla2(kwuargs['directorioSalida'],xmlEntradaObject.tipo,idItem, plantillaSalida,'xml',formato,estilo,merge=raiz)
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
tipoPregunta='definicion'
listaXmlEntrada=list()

# Almacenamiento usando el parser para este tipo de pregunta

#Ahora la entrada que indica la cantidad de alternativas viene incrustada como atributo en los respectivos
#XML de entrada
#cantidadAlternativas=xmlSalida.argParse()

if raiz=='merge':
    xmlSalida.mergeOperation(nombreDirectorioSalidas+'/'+tipoPregunta,tipoPregunta,'xml','open',formato,estilo)

if nombres.validaExistenciaArchivo(nombreDirectorioEntradas)==True:
    listaXmlEntrada=xmlSalida.lecturaXmls(nombreDirectorioEntradas, tipoPregunta)

for cadaXmlEntrada in listaXmlEntrada:
    retornaPlantilla(nombreDirectorioPlantillas, cadaXmlEntrada, cadaXmlEntrada.cantidadAlternativas,tipoPregunta,raiz,formato,estilo, directorioSalida=nombreDirectorioSalidas+'/'+tipoPregunta)
    
if raiz=='merge':
    xmlSalida.mergeOperation(nombreDirectorioSalidas+'/'+tipoPregunta,tipoPregunta,'xml','close',formato,estilo)