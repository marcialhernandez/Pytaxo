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

import os, sys,subprocess, hashlib, ast,argparse
sys.path.insert(0, os.getcwd())
from archivos import nombres, xmlSalida,acceso
from clases import plantilla

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

def borraHijos(ETObject):
    for elem in ETObject.getchildren():
        ETObject.remove(elem)
    pass
    
def generaGlosaEntradas(listaEntradasBrutas):
    glosaIntermedia=""
    listaEntradas=listaEntradasBrutas.split(";")
    cantidadEntradas=len(listaEntradas)
    if cantidadEntradas>1:
        contador=0
        for entrada in listaEntradas:
            if contador==0:
                glosaIntermedia+="las entradas "+entrada
                contador+=1
            else:
                if contador==cantidadEntradas-1:
                    glosaIntermedia+=" y "+entrada
                    contador+=1
                else:
                    glosaIntermedia+=", "+entrada
                    contador+=1
        return glosaIntermedia
    else:
        glosaIntermedia="la entrada "+listaEntradas[0].rstrip().lstrip()
        return glosaIntermedia

def ejecutaPyTemporal(archivoTemporal):
    nombreTemporal=archivoTemporal.name
    directorioTemporal=nombreTemporal.split("/")
    directorioTemporal.pop()
    directorioTemporal='/'.join(directorioTemporal)
    directorioTemporal=nombres.directorioReal(directorioTemporal)
    p = subprocess.Popen(["python",nombreTemporal],stdout=subprocess.PIPE, cwd=directorioTemporal)
    return str(p.communicate()[0]) #obtiene solo los resultados y no los errores 

#entradas:
#enunciado: obtenido de la respectiva plantilla
#contadorEntradasBruto: indica que entrada se esta ejecutando en la actual traza
#plantillaSalida: Es la plantilla estandar en donde se guarda toda la info en el xml de salida
#codigoPython: diccionario que contiene toda la info del codigo examinado obtenido desde la entrada xml
def incluyeInfo(codigoPython,plantillaSalida,contadorEntradasBruto,enunciado,streamTraza,seccionRetroalimentacion):
    idXmlSalida=codigoPython["id"]+'+'+str(hashlib.sha256(codigoPython["entradasBruto"][contadorEntradasBruto]).hexdigest())+'+'+codigoPython["entradasBruto"][contadorEntradasBruto]
    segundaParteEnunciado="Con "+generaGlosaEntradas(codigoPython["entradasBruto"][contadorEntradasBruto]).rstrip().lstrip()+"."
    enunciado=enunciado.replace("@nombreFuncion", codigoPython["nombreFuncionPrincipal"]).rstrip().lstrip()+" "+segundaParteEnunciado.rstrip().lstrip()
    for elem in plantillaSalida.iterfind('generalfeedback'):
        plantillaSalida.remove(elem)
    for elem in plantillaSalida.getchildren():
        if elem.tag=='questiontext':
            for elem2 in elem.iterfind('text'):
                for elem3 in elem2.getchildren():
                    elem2.remove(elem3)
                elem2.append(ET.Comment((' --><![CDATA[' + ('\n<h2>'+enunciado+'</h2><BR>\n\n'+'<pre><code class="codeblock">\n'+codigoPython["codigoBruto"]+'\n</code></pre>').replace(']]>', ']]]]><![CDATA[>')) + ']]><!-- '))
                #elem2.text='<![CDATA[<h2>'+enunciado+'</h2><pre><code class="codeblock">'+codigoPython["codigoBruto"]+'</code></pre>'#+']]>'
    generalfeedback=ET.SubElement(plantillaSalida,'generalfeedback')
    generalfeedbackText=ET.SubElement(generalfeedback,'text')
    seccionRetroalimentacion.text=codigoPython["comentarios"].lstrip()+'\n\n'+streamTraza
    return idXmlSalida

def mergeLineas(listaLineasTraza):
    traza=""
    for linea in listaLineasTraza:
        traza=traza+linea+'\n'
    traza.rstrip('\n').rstrip()
    return traza

def estandarizaLineas(listaLineasTraza,nombreFuncionPrincipal):
    listaTraza=list()
    for linea in listaLineasTraza:
        if linea["evento"]=='call':
            linea="L"+str(linea["numLinea"])+': '+"Se llama a la funcion:"+linea["invocacion"]
            listaTraza.append(linea)
        elif linea["evento"]=='line':
            stack=""
            for key in linea['varLocales'].keys():
                stack=stack+str(key)+':'+str(linea['varLocales'][key])+', '
            stack.rstrip(',').rstrip()
            if nombreFuncionPrincipal in linea['funcionProcedencia']:
                linea="L"+str(linea["numLinea"])+': '+linea["linea"]+" - Mem: "+stack
            else:
                linea="L"+str(linea["numLinea"])+': '+linea["linea"]+" - Mem: "+stack+" - Funcion de procedencia: "+linea['funcionProcedencia']
            listaTraza.append(linea)
        elif linea["evento"]=='return':
            linea="L"+str(linea["numLinea"])+': Funcion: '+linea['funcionProcedencia']+ ' - retorna: '+str(linea['retorno'])
            listaTraza.append(linea)
        elif linea["evento"]=='exception':
            linea="Error en linea "+str(linea["numLinea"])+': '+linea["linea"]+', de la funcion: '+linea['funcionProcedencia']+', '+linea["tipo"]+': '+linea['glosa']
            listaTraza.append(linea)  
    return listaTraza

def normalizaLineas(listaLineasTraza):
    offsetNorma=listaLineasTraza[0]["numLinea"]-1
    for linea in listaLineasTraza:
        if linea["numLinea"]-1<offsetNorma:
            offsetNorma=linea["numLinea"]-1
    for linea in listaLineasTraza:
        linea["numLinea"]=linea["numLinea"]-offsetNorma

def obtieneTraza(datosSalidaSubproceso):
    datosSalidaSubproceso=datosSalidaSubproceso.split('\n')
    largoStream=len(datosSalidaSubproceso)
    contador=0
    listaLineasTraza=list()
    banderaAgregaLinea=True
    banderaBreak=False
    #Ya que al momento de splitear por saltos de linea
    #el ultimo elemento es un EOF, asi que se recorre hasta el penultimo elemento
    while contador!=largoStream-1:
        try:
            linea=ast.literal_eval(datosSalidaSubproceso[contador])
        except:
            linea=None #ignorar los prints
        contador+=1
        if type(linea) is dict:
            linea["numLinea"]=ast.literal_eval(linea["numLinea"])
            if "evento" in linea.keys():
                if linea["evento"]=='line':
                    linea["identacion"]=int(linea["identacion"])
                    linea["varLocales"]=ast.literal_eval(linea["varLocales"]) #listo!
                    linea["varGlobales"]=ast.literal_eval(linea["varGlobales"])
                    linea["argumentos"]=ast.literal_eval(linea["argumentos"])
                    if "_run_exitfuncs" in linea["funcionProcedencia"]:
                        banderaAgregaLinea=False
                elif linea["evento"]=='return':
                    try:
                        linea["retorno"]=ast.literal_eval(linea["retorno"])
                    except:
                        pass
                    if "_run_exitfuncs" in linea["funcionProcedencia"]:
                        banderaAgregaLinea=False
                    if linea["retorno"]=="infinito":
                        banderaBreak==True
                elif linea["evento"]=='call':
                    if "_run_exitfuncs" in linea["invocacion"] or "_remove" in linea["invocacion"]:
                        banderaAgregaLinea=False
            if banderaAgregaLinea==True:
                listaLineasTraza.append(linea)
            if banderaBreak==True:
                break;
    return listaLineasTraza

#Funcion que analiza la plantilla que corresponde a este tipo de pregunta
#A esa plantilla se le anaden los datos obtenidos desde la entrada de
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
            plantillasValidas.append(plantilla.plantilla(tipoPregunta,enunciado.rstrip(),taxo=taxonomia))
            validaPlantilla=False
    return plantillasValidas

def retornaPlantilla(nombreDirectorioPlantillas,xmlEntradaObject,cantidadAlternativas, tipoPregunta,raiz,formato,estilo, **kwuargs): #,xmlEntradaObject):
    contador=0
    banderaEstado=False
    enunciado=""
    if 'directorioSalida' in kwuargs.keys():
        banderaEstado=True #Indica si se debe imprimir o no el estado de la cantidad de salidas
    for plantilla in recogePlantillas(nombreDirectorioPlantillas,tipoPregunta):
        plantillaSalida=xmlSalida.plantillaGenericaSalida(xmlEntradaObject.puntaje,xmlEntradaObject.shuffleanswers,xmlEntradaObject.penalty,xmlEntradaObject.answernumbering)
        plantillaSalida.set('tipo',xmlEntradaObject.tipo)
        #unico tipo de item que cambia
        plantillaSalida.set('type',"essay")
        answer=ET.SubElement(plantillaSalida,'answer')
        answer.set('fraction',"0")
        answerFeedback=ET.SubElement(answer,'feedback')
        answerFeedbackText=ET.SubElement(answerFeedback,'text')
        plantillaSalida.set('idOrigenEntrada',xmlEntradaObject.idOrigenEntrada)
        plantillaSalida.set('taxonomia',plantilla.taxo)
        responsefieldlines=ET.SubElement(plantillaSalida,'responsefieldlines')
        responsefieldlines.text="300"
        for codigoPython in xmlEntradaObject.codigos:
            #lista de archivos temporales por entrada anidada al codigo
            contadorEntradasBruto=0
            glosaEnunciado=""
            for archivoTemporal in codigoPython["codigo"]:
                streamTraza=obtieneTraza(ejecutaPyTemporal(archivoTemporal))
                if len(streamTraza)>0:
                    normalizaLineas(streamTraza)#Normaliza numero de lineas
                else:
                    banderaEstado="No trazable"
                streamTraza=estandarizaLineas(streamTraza,codigoPython["nombreFuncionPrincipal"])#Pasa las lineas a formato String
                idXmlSalida=incluyeInfo(codigoPython,plantillaSalida,contadorEntradasBruto,plantilla.enunciado[:],mergeLineas(streamTraza),answerFeedbackText)
                if banderaEstado==True:
                    id=str(xmlEntradaObject.idOrigenEntrada)+"."+idXmlSalida
                    plantillaSalida.set('id',id)
                    for elem in plantillaSalida.getchildren():
                        if elem.tag=='name':
                            for elem2 in elem.iterfind('text'):
                                elem2.text=plantilla.taxo+"-"+id
                    if raiz=='quiz':
                        quiz = ET.Element('quiz')
                        quiz.append(plantillaSalida)
                        xmlSalida.escribePlantilla2(kwuargs['directorioSalida'],xmlEntradaObject.tipo,id,quiz,'xml',formato,estilo,merge=raiz)
                    else:
                        xmlSalida.escribePlantilla2(kwuargs['directorioSalida'], xmlEntradaObject.tipo,id,plantillaSalida,'xml',formato,estilo,merge=raiz)
                    contador+=1
                elif banderaEstado==False:
                    print ET.tostring(plantillaSalida, 'utf-8', method="xml")
                    contador+=1
                else:
                    print "Error 13: La funcion '"+codigoPython["nombreFuncionPrincipal"] +"' o su entrada: '"+codigoPython["entradasBruto"][contadorEntradasBruto]+"' presenta una falla y no se puede Trazar"
                    banderaEstado=True
                contadorEntradasBruto+=1
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
tipoPregunta='pythonTraza'
listaXmlEntrada=list()

if raiz=='merge':
    xmlSalida.mergeOperation(nombreDirectorioSalidas+'/'+tipoPregunta,tipoPregunta,'xml','open',formato,estilo)

if nombres.validaExistenciaArchivo(nombreDirectorioEntradas)==True:
    listaXmlEntrada=xmlSalida.lecturaXmls(nombreDirectorioEntradas, tipoPregunta)

for cadaXmlEntrada in listaXmlEntrada:
    retornaPlantilla(nombreDirectorioPlantillas, cadaXmlEntrada, cadaXmlEntrada.cantidadAlternativas,tipoPregunta,raiz,formato,estilo, directorioSalida=nombreDirectorioSalidas+'/'+tipoPregunta)
    
if raiz=='merge':
    xmlSalida.mergeOperation(nombreDirectorioSalidas+'/'+tipoPregunta,tipoPregunta,'xml','close',formato,estilo)