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

import os, sys,subprocess, hashlib, copy, itertools, ast,argparse
sys.path.insert(0, os.getcwd())

from archivos import nombres, xmlSalida,acceso
from clases import plantilla

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

def generaGlosaIteraciones(stringIteraciones):
    if int(stringIteraciones)>1:
        return stringIteraciones+" iteraciones"
    else:
        return stringIteraciones+" iteracion"

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
        glosaIntermedia="la entrada "+listaEntradas[0]
        return glosaIntermedia
        

def mergeKeyValue2niveles(dictObject):
    stringFromDict=""
    if type(dictObject.values()[0])!=type(dict()):
        return mergeKeyValue(dictObject)
    else:
        for llave in dictObject.values()[0].keys():           
                stringFromDict+=str(llave)+" = " +str( dictObject.values()[0][llave]) + ", "
        stringFromDict=str(dictObject.keys()[0])+" : "+stringFromDict
        return stringFromDict.rstrip(", ")

def mergeKeyValue(dictObject):
    stringFromDict=""
    for llave in dictObject.keys():
        stringFromDict+=str(llave)+" = "+str(dictObject[llave])+", "
    return stringFromDict.rstrip(", ")

def borraHijos(ETObject):
    for elem in ETObject.getchildren():
        ETObject.remove(elem)
    pass

#dictIteracion es del tipo {numeroIteracion:dict con var locales}
def agregaAlternativaIteracion(ETObject,dicIteracion,tipo,puntaje):
    seccionAlternativa=ET.SubElement(ETObject,'answer')
    seccionAlternativaText=ET.SubElement(seccionAlternativa,'text')
    seccionAlternativaFeedback=ET.SubElement(seccionAlternativa,'feedback')
    seccionAlternativaFeedbackText=ET.SubElement(seccionAlternativaFeedback,'text')
    seccionAlternativaText.text=str(mergeKeyValue(dicIteracion.values()[0]))
    seccionAlternativa.set('id',str(dicIteracion.keys()[0]))
    seccionAlternativa.set('tipo',tipo)
    seccionAlternativa.set('puntaje',puntaje)
    if tipo=="solucion":
        seccionAlternativa.set('fraction',"100")
        return "s."+str(dicIteracion.keys()[0])
    else:
        seccionAlternativa.set('fraction',"0")
        return "d."+str(dicIteracion.keys()[0])

#Reparar pues mal funciona para ciclos infinitos
def buscaIteracionAAnalizar(datoStreamTraza,lineaIterativa):
    listaTrazasLineaIterativa=list()
    banderaExisteIteracion=False
    cuentaIteraciones=0 #indica cuantas iteraciones realiza la condicion raiz
    for diccionarioLinea in datoStreamTraza:
        if diccionarioLinea["evento"]=="line":
            if lineaIterativa in diccionarioLinea["linea"]:
                #Si la identacion es mayor que la raiz o si es igual y contiene el enunciado de la raiz, se guardara la linea, el stack y el valor actual de cuenta iteraciones en una lista
                listaTrazasLineaIterativa.append(dict({cuentaIteraciones:diccionarioLinea["varLocales"]}))
                cuentaIteraciones+=1
                if banderaExisteIteracion==False:
                    banderaExisteIteracion=True
        if cuentaIteraciones>15: #MAX VECINDAD
            break
    return listaTrazasLineaIterativa,banderaExisteIteracion,cuentaIteraciones

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
#incluyeInfo(codigoPython,plantillaSalida,contadorEntradasBruto,copy.copy(plantilla.enunciado),numerosIteracion.rstrip("+"),listaTrazasLineaIterativa[:],cantidadCiclosConsulta)
def incluyeInfo(codigoPython,plantillaSalida,contadorEntradasBruto,enunciado,numerosIteracion,listaTrazasLineaIterativa, actualCantidadCiclosConsulta):
    idXmlSalida=""
    idEntradaBruta=str(hashlib.sha256(codigoPython["codigoEnunciado"][contadorEntradasBruto]).hexdigest())
    plantillaSalida.set('entradas', codigoPython["entradasBruto"][contadorEntradasBruto])
    plantillaSalida.set('combinacionAlternativas', numerosIteracion)
    idXmlSalida=idEntradaBruta+'+'+numerosIteracion
    enunciado=enunciado.replace("@iteracion",codigoPython["lineaIterativa"])
    enunciado=enunciado.replace("@entrada",generaGlosaEntradas(codigoPython["entradasBruto"][contadorEntradasBruto]))
    enunciado=enunciado.replace("@funcionPrincipal",codigoPython["nombreFuncionPrincipal"])
    enunciado=enunciado.replace("@numIteraciones",generaGlosaIteraciones(actualCantidadCiclosConsulta))
    glosaSolucion=""
    indicaPrimero=True
    for elem in listaTrazasLineaIterativa:
        if indicaPrimero==True:     
            glosaSolucion+="Traza\nNumero de iteracion: Memoria\n"
            indicaPrimero=False
        glosaSolucion+=mergeKeyValue2niveles(elem)+"\n"
    glosaSolucion.strip()
    for elem in plantillaSalida.iterfind('generalfeedback'):
        plantillaSalida.remove(elem)
    for elem in plantillaSalida.getchildren():
        if elem.tag=='questiontext':
            for elem2 in elem.iterfind('text'):
                for elem3 in elem2.getchildren():
                    elem2.remove(elem3)
                elem2.append(ET.Comment((' --><![CDATA[' + ('\n<h2>'+enunciado+'</h2><BR>\n\n'+'<pre><code class="codeblock">\n'+codigoPython["codigoEnunciado"]+'\n</code></pre>').replace(']]>', ']]]]><![CDATA[>')) + ']]><!-- '))
                #elem2.text='<![CDATA[<h2>'+enunciado+'</h2><pre><code class="codeblock">'+codigoPython["codigoBruto"]+'</code></pre>'
    generalfeedback=ET.SubElement(plantillaSalida,'generalfeedback')
    generalfeedbackText=ET.SubElement(generalfeedback,'text')
    generalfeedbackText.text=codigoPython["comentarios"]+'\n\n'+glosaSolucion
    return idXmlSalida

def mergeLineas(listaLineasTraza):
    traza=""
    for linea in listaLineasTraza:
        traza=traza+linea+'\n'
    traza.rstrip('\n').rstrip()
    return traza

def estandarizaLineas(listaLineasTraza):
    listaTraza=list()
    for linea in listaLineasTraza:
        if linea["evento"]=='call':
            linea="Linea:"+str(linea["numLinea"])+': '+"Se invoca a funcion:"+linea["invocacion"]
            listaTraza.append(linea)
        elif linea["evento"]=='line':
            stack=""
            for key in linea['varLocales'].keys():
                stack=stack+str(key)+':'+str(linea['varLocales'][key])+', '
            stack.rstrip(',').rstrip() 
            linea="Linea:"+str(linea["numLinea"])+': '+linea["linea"]+" - Mem: "+stack+" - Funcion de procedencia: "+linea['funcionProcedencia']
            listaTraza.append(linea)
        elif linea["evento"]=='return':
            linea="Linea:"+str(linea["numLinea"])+': Funcion: '+linea['funcionProcedencia']+ ' - retorna: '+str(linea['retorno'])
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
    id=""
    plantillasValidas=list()
    for archivoPlantilla in nombres.especificDirectoryNames(nombreDirectorioPlantillas):
        nombreDirectorioArchivoPlantilla=nombres.directorioReal(nombreDirectorioPlantillas+"/"+archivoPlantilla)
        arbolXmlPlantillaEntrada = ET.ElementTree() # instantiate an object of *class* `ElementTree`
        arbolXmlPlantillaEntrada.parse(nombreDirectorioArchivoPlantilla)
        #arbolXml=ET.ElementTree(file=nombreDirectorioArchivoPlantilla)
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
                    enunciado=enunciado+subRaiz.text
                if subRaiz.tag=='termino':
                    enunciado=enunciado+' @termino'
            plantillasValidas.append(plantilla.plantilla(tipoPregunta,enunciado.rstrip(),id,taxo=taxonomia))
            validaPlantilla=False
    return plantillasValidas

def retornaPlantilla(nombreDirectorioPlantillas,xmlEntradaObject,cantidadAlternativas, tipoPregunta,raiz,formato,estilo, **kwuargs): #,xmlEntradaObject):
    contador=0
    banderaEstado=False
    enunciado=""
    if 'directorioSalida' in kwuargs.keys():
        banderaEstado=True #Indica si se debe imprimir o no el estado de la cantidad de salidas
    for plantilla in recogePlantillas(nombreDirectorioPlantillas,tipoPregunta):
        if xmlEntradaObject.linkPlantilla(plantilla)==False:
            continue
        plantillaSalida=xmlSalida.plantillaGenericaSalida(xmlEntradaObject.puntaje,xmlEntradaObject.shuffleanswers,xmlEntradaObject.penalty,xmlEntradaObject.answernumbering)
        plantillaSalida.set('tipo',xmlEntradaObject.tipo)
        plantillaSalida.set('id',xmlEntradaObject.id)
        plantillaSalida.set('idOrigenEntrada',xmlEntradaObject.idOrigenEntrada)
        plantillaSalida.set('taxonomia',plantilla.taxo)
        for codigoPython in xmlEntradaObject.codigos:
            contadorEntradasBruto=0
            glosaEnunciado=""
            for archivoTemporal in codigoPython["codigo"]:
                idXmlSalida=""
                streamTraza=obtieneTraza(ejecutaPyTemporal(archivoTemporal))
                if len(streamTraza)>0:
                    normalizaLineas(streamTraza)#Normaliza numero de lineas
                    banderaEstado=True
                else:
                    banderaEstado="No trazable"
                #Si fue trazable
                if banderaEstado==True and "lineaIterativa" in codigoPython.keys() and len(codigoPython["cantidadCiclosConsulta"])>0:
                    try:
                        listaTrazasLineaIterativa,banderaExisteIteracion,cuentaIteraciones=buscaIteracionAAnalizar(streamTraza,codigoPython["lineaIterativa"])
                    except:
                        print "Error 8: No se ha especificado linea iterativa para la funcion '"+str(codigoPython["nombreFuncionPrincipal"])+"'" 
                        continue
                             
                    if banderaExisteIteracion==False:
                        print "Error 9: La sentencia '"+codigoPython["lineaIterativa"]+"' no aparece en la funcion "+codigoPython["nombreFuncionPrincipal"]
                        contadorEntradasBruto+=1
                        continue
                    
                    if banderaEstado=="No trazable":
                        #print "Error: La entrada: "+codigoPython["entradasBruto"][contadorEntradasBruto]+" presenta una falla y no se puede Trazar"
                        print "Error 13: La funcion '"+codigoPython["nombreFuncionPrincipal"] +"' o su entrada: '"+codigoPython["entradasBruto"][contadorEntradasBruto]+"' presenta una falla y no se puede Trazar"
                        banderaEstado=False
                        contadorEntradasBruto+=1
                        continue
                    
                    #print listaTrazasLineaIterativa
                    cantidadLineasTrazaIterativa=len(listaTrazasLineaIterativa)

                    for cantidadCiclosConsulta in codigoPython["cantidadCiclosConsulta"]:
                        
                        if cantidadLineasTrazaIterativa<int(cantidadCiclosConsulta):
                            print "Error 11: No se pueden crear preguntas indicando memoria de la iteracion "+str(cantidadCiclosConsulta)+" cuando solo se generan "+str(cantidadLineasTrazaIterativa-1)+" iteraciones"
                        elif cantidadLineasTrazaIterativa-2<int(xmlEntradaObject.cantidadAlternativas):
                            print "Error 7: No se pueden crear preguntas con la entrada: "+codigoPython["entradasBruto"][contadorEntradasBruto]+" - No genera las suficentes iteraciones para crear distractores"
                        else:
                            copiaListaTrazasLineaIterativa=listaTrazasLineaIterativa[:]
                            alternativaCorrecta=copy.copy(copiaListaTrazasLineaIterativa[int(cantidadCiclosConsulta)])
                            del copiaListaTrazasLineaIterativa[int(cantidadCiclosConsulta)]
                            #Se quita el primero pues es de la iteracion 0
                            copiaListaTrazasLineaIterativa=copiaListaTrazasLineaIterativa[1:]
                            #-1 pues la alternativa correcta se agrega de forma posterior
                            try:
                                listaCombinacionesAlternativas=list(itertools.combinations(copiaListaTrazasLineaIterativa,int(xmlEntradaObject.cantidadAlternativas)-1))
                            except:
                                print "Error 4: Este tipo de item no soporta 0 alternativas como argumento de entrada"
                                exit() 
                            for cadaCombinacion in listaCombinacionesAlternativas:
                                #contador de cantidad de archivos de salida
                                contador+=1
                                #menciona las iteraciones de cada alternativa separados por una +
                                numerosIteracion=""
                                for distractor in cadaCombinacion:
                                #se agrega al pozo de alternativas con algun identificador, identificando que son distractores y senalando tambien en el root de la alternativas, con que entrada y que funcion fue hecha
                                    numerosIteracion+=agregaAlternativaIteracion(plantillaSalida,distractor,"distractor","0")+"+"
                                numerosIteracion+=agregaAlternativaIteracion(plantillaSalida,alternativaCorrecta,"solucion",str(xmlEntradaObject.puntaje))+"+"
                            
                                idXmlSalida=incluyeInfo(codigoPython,plantillaSalida,contadorEntradasBruto,copy.copy(plantilla.enunciado),numerosIteracion.rstrip("+"),listaTrazasLineaIterativa[:],cantidadCiclosConsulta)
                                
                                if banderaEstado==True:
                                    id= xmlEntradaObject.idItem(plantilla,tipoPregunta,codigoPython["nombreFuncionPrincipal"]+"_"+idXmlSalida)
                                    #id=xmlEntradaObject.idOrigenEntrada+"-"+codigoPython["nombreFuncionPrincipal"]+"-"+idXmlSalida
                                    for elem in plantillaSalida.getchildren():
                                        if elem.tag=='name':
                                            for elem2 in elem.iterfind('text'):
                                                elem2.text=id
                                    if raiz=='quiz':
                                        quiz = ET.Element('quiz')
                                        quiz.append(plantillaSalida)
                                        xmlSalida.escribePlantilla2(kwuargs['directorioSalida'],xmlEntradaObject.tipo,id,quiz,'xml',formato,estilo,merge=raiz)
                                    else:
                                        xmlSalida.escribePlantilla2(kwuargs['directorioSalida'],xmlEntradaObject.tipo,id,copy.copy(plantillaSalida),'xml',formato,estilo,merge=raiz)
                                else:
                                    pass
                                for elem in plantillaSalida.getchildren():
                                    if elem.tag=='answer':
                                        plantillaSalida.remove(elem)    
                
                #La bandera se setea a False por cada archivo temporal que se comprueba
                banderaEstado=False
                contadorEntradasBruto+=1
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
tipoPregunta='pythonIterativo'
listaXmlEntrada=list()

if raiz=='merge':
    xmlSalida.mergeOperation(nombreDirectorioSalidas+'/'+tipoPregunta,tipoPregunta,'xml','open',formato,estilo)

if nombres.validaExistenciaArchivo(nombreDirectorioEntradas)==True:
    listaXmlEntrada=xmlSalida.lecturaXmls(nombreDirectorioEntradas, tipoPregunta)

for cadaXmlEntrada in listaXmlEntrada:
    retornaPlantilla(nombreDirectorioPlantillas, cadaXmlEntrada, cadaXmlEntrada.cantidadAlternativas,tipoPregunta,raiz,formato,estilo, directorioSalida=nombreDirectorioSalidas+'/'+tipoPregunta)
    
if raiz=='merge':
    xmlSalida.mergeOperation(nombreDirectorioSalidas+'/'+tipoPregunta,tipoPregunta,'xml','close',formato,estilo)