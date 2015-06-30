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

import os, sys,subprocess, hashlib, copy, itertools, ast
sys.path.insert(0, os.getcwd())

from archivos import nombres, xmlSalida, acceso
from clases import alternativa, plantilla


try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

def generaAlternativaCorrecta(alternativaCorrecta,puntaje):
    #xmlEntradaObject.puntaje
    #Si genera 8 iteraciones
    if alternativaCorrecta.keys()[0]<9:
        #entonces
        if alternativaCorrecta.keys()[0]==8:
            return alternativa.alternativa(str(alternativaCorrecta.keys()[0]),"solucion", puntaje,"alternativa correcta")
            
        elif alternativaCorrecta.keys()[0]<8 and alternativaCorrecta.keys()[0]>2:
            return alternativa.alternativa(str(alternativaCorrecta.keys()[0]),"solucion", puntaje,"alternativa correcta")
           
        elif alternativaCorrecta.keys()[0]==2:
            return alternativa.alternativa(str(alternativaCorrecta.keys()[0]),"solucion", puntaje,"alternativa correcta")
            #para el caso en que solo se haga 1 iteracion
        else:
            return alternativa.alternativa(str(alternativaCorrecta.keys()[0]),"solucion", puntaje,"alternativa correcta")
    elif alternativaCorrecta.keys()[0]==9:
        return alternativa.alternativa(str(alternativaCorrecta.keys()[0]),"solucion", puntaje,"alternativa correcta")
        #Para el caso que realice mas de 9 iteraciones
    else:
        return alternativa.alternativa("10 iteraciones o mas","solucion", puntaje,"alternativa Incorrecta. Desfase de 2 o mas iteraciones")

def generaPozoAlternativas(alternativaCorrecta):
    pozoDistractores=list()
    #Si genera 8 iteraciones
    if alternativaCorrecta.keys()[0]<9:
        #entonces
        if alternativaCorrecta.keys()[0]==8:
            pozoDistractores.append(alternativa.alternativa(str(alternativaCorrecta.keys()[0]+1),"distractor", 0,"alternativa Incorrecta. Desfase de 1 iteracion"))
            pozoDistractores.append(alternativa.alternativa("10 iteraciones o mas","distractor", 0,"alternativa Incorrecta. Desfase de 2 o mas iteraciones"))
            pozoDistractores.append(alternativa.alternativa(str(alternativaCorrecta.keys()[0]-1),"distractor", 0,"alternativa Incorrecta. Desfase de 1 iteracion"))
            pozoDistractores.append(alternativa.alternativa(str(alternativaCorrecta.keys()[0]-2),"distractor", 0,"alternativa Incorrecta. Desfase de 2 iteraciones"))
        elif alternativaCorrecta.keys()[0]<8 and alternativaCorrecta.keys()[0]>2:
            pozoDistractores.append(alternativa.alternativa(str(alternativaCorrecta.keys()[0]+1),"distractor", 0,"alternativa Incorrecta. Desfase de 1 iteracion"))
            pozoDistractores.append(alternativa.alternativa(str(alternativaCorrecta.keys()[0]+2),"distractor", 0,"alternativa Incorrecta. Desfase de 2 iteraciones"))
            pozoDistractores.append(alternativa.alternativa(str(alternativaCorrecta.keys()[0]-1),"distractor", 0,"alternativa Incorrecta. Desfase de 1 iteracion"))
            pozoDistractores.append(alternativa.alternativa(str(alternativaCorrecta.keys()[0]-2),"distractor", 0,"alternativa Incorrecta. Desfase de 2 iteraciones"))
        elif alternativaCorrecta.keys()[0]==2:
            pozoDistractores.append(alternativa.alternativa(str(alternativaCorrecta.keys()[0]+1),"distractor", 0,"alternativa Incorrecta. Desfase de 1 iteracion"))
            pozoDistractores.append(alternativa.alternativa(str(alternativaCorrecta.keys()[0]+2),"distractor", 0,"alternativa Incorrecta. Desfase de 2 iteraciones"))
            pozoDistractores.append(alternativa.alternativa(str(alternativaCorrecta.keys()[0]-1),"distractor", 0,"alternativa Incorrecta. Desfase de 1 iteracion"))
            #para el caso en que solo se haga 1 iteracion
        else:
            pozoDistractores.append(alternativa.alternativa(str(alternativaCorrecta.keys()[0]+1),"distractor", 0,"alternativa Incorrecta. Desfase de 1 iteracion"))
            pozoDistractores.append(alternativa.alternativa(str(alternativaCorrecta.keys()[0]+2),"distractor", 0,"alternativa Incorrecta. Desfase de 2 iteraciones"))
            pozoDistractores.append(alternativa.alternativa(str(alternativaCorrecta.keys()[0]+2),"distractor", 0,"alternativa Incorrecta. Desfase de 3 iteraciones"))
    elif alternativaCorrecta.keys()[0]==9:
        pozoDistractores.append(alternativa.alternativa("10 iteraciones o mas","distractor", 0,"alternativa Incorrecta. Desfase de 2 o mas iteraciones"))
        pozoDistractores.append(alternativa.alternativa(str(alternativaCorrecta.keys()[0]-1),"distractor", 0,"alternativa Incorrecta. Desfase de 1 iteracion"))
        pozoDistractores.append(alternativa.alternativa(str(alternativaCorrecta.keys()[0]-2),"distractor", 0,"alternativa Incorrecta. Desfase de 2 iteraciones"))
        #Para el caso que realice mas de 9 iteraciones
    else:
        pozoDistractores.append(alternativa.alternativa("9","distractor", 0,"alternativa Incorrecta. Desfase de 1 iteracion"))
        pozoDistractores.append(alternativa.alternativa("8","distractor", 0,"alternativa Incorrecta. Desfase de 2 iteraciones"))
        pozoDistractores.append(alternativa.alternativa("7","distractor", 0,"alternativa Incorrecta. Desfase de 3 iteraciones"))
    return pozoDistractores

def generaGlosaIteraciones(stringIteraciones):
    if int(stringIteraciones)>1:
        return stringIteraciones+" iteraciones"
    else:
        return stringIteraciones+" iteracion"

def generaGlosaEntradas(listaEntradasBrutas):
    glosaIntermedia=""
    #listaEntradas=codigoPython["entradasBruto"][contadorEntradasBruto].split(";")
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

def agregaAlternativaIteracion(ETObject,alternativaObject):
    seccionAlternativa=ET.SubElement(ETObject,'alternativa')
    seccionAlternativa.text=alternativaObject.llave
    seccionAlternativa.set('numeroIteracion', alternativaObject.llave)
    seccionAlternativa.set('tipo',alternativaObject.tipo)
    seccionAlternativa.set('puntaje',str(alternativaObject.puntaje))
    seccionAlternativaComentario=ET.SubElement(seccionAlternativa,'comentario')
    seccionAlternativaComentario.text=alternativaObject.glosa
    return alternativaObject.llave

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
        #Para saber si la funcion tiende a infinito con la entrada
        #Aunque esto no quiere decir que el ciclo actual que se busca sea el que produce la divergencia en la funcion
        elif diccionarioLinea["evento"]=="return":
            if diccionarioLinea["retorno"]=="infinito":
                listaTrazasLineaIterativa.append(dict({cuentaIteraciones:diccionarioLinea["retorno"]}))        
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
def incluyeInfo(codigoPython,seccionSolucion,seccionAlternativas,plantillaSalida,contadorEntradasBruto,enunciado,numerosIteracion,listaTrazasLineaIterativa):
    idXmlSalida=""
    idEntradaBruta=str(hashlib.sha256(codigoPython["entradasBruto"][contadorEntradasBruto]).hexdigest())
    seccionAlternativas.set('id', idEntradaBruta)
    seccionAlternativas.set('entradas', codigoPython["entradasBruto"][contadorEntradasBruto])
    seccionAlternativas.set('combinacionAlternativas', numerosIteracion)
    for subRaizAux in plantillaSalida.iter():
        if subRaizAux.tag=='plantilla':
            idXmlSalida=str(codigoPython["id"])+'-'+idEntradaBruta+'-'+numerosIteracion
            subRaizAux.set('id',idXmlSalida)
        if subRaizAux.tag=='enunciado':
            enunciado=enunciado.replace("@iteracion",codigoPython["lineaIterativa"])
            enunciado=enunciado.replace("@entrada",generaGlosaEntradas(codigoPython["entradasBruto"][contadorEntradasBruto]))
            enunciado=enunciado.replace("@funcionPrincipal",codigoPython["nombreFuncionPrincipal"])
            subRaizAux.text=enunciado
    borraHijos(seccionSolucion)
    seccionComentarios=ET.SubElement(seccionSolucion,'comentarios')
    seccionComentarios.text=codigoPython["comentarios"]
    glosaSolucion=""
    indica10=False
    largoListaTrazasLineaIterativa=len(listaTrazasLineaIterativa)
    contador=0
    for elem in listaTrazasLineaIterativa:
        if contador==0:
            glosaSolucion+="Traza\nNumero de iteracion: Memoria\n"             
        glosaSolucion+=mergeKeyValue2niveles(elem)+"\n"
        contador+=1
        if contador==largoListaTrazasLineaIterativa-1:
            glosaSolucion+="------------------------Solucion------------------------"+"\n"
        elif contador==largoListaTrazasLineaIterativa:
            glosaSolucion+="--------------------------------------------------------"+"\n"
        elif contador>9:
            indica10=True
            break
    if indica10==True:
        glosaSolucion+="------------------------Solucion------------------------"+"\n"
        glosaSolucion+="mas de 10 iteraciones\n"
        glosaSolucion+="--------------------------------------------------------"+"\n"
    glosaSolucion.strip()
    seccionSolucion.text=glosaSolucion
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
                    #print type(linea["argumentos"])
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
    contador=0
    banderaEstado=False
    enunciado=""
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
                    enunciado=plantilla.enunciado[:]
                    #subRaizSalida.text=plantilla.enunciado
                if subRaizSalida.tag=='opciones':
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
                                print "Error 11: La entrada: "+str(codigoPython["entradasBruto"][contadorEntradasBruto])+" presenta una falla y no se puede Trazar"
                                banderaEstado=False
                                contadorEntradasBruto+=1
                                continue
                            
                            #Si fue trazable
                            if banderaEstado==True and "lineaIterativa" in codigoPython.keys():
                                try:
                                    listaTrazasLineaIterativa,banderaExisteIteracion,cuentaIteraciones=buscaIteracionAAnalizar(streamTraza,codigoPython["lineaIterativa"])
                                except:
                                    print "Error 8: No se ha especificado linea iterativa para la funcion '"+codigoPython["nombreFuncionPrincipal"]+"'"
                                    contadorEntradasBruto+=1
                                    continue     
                                if banderaExisteIteracion==False:
                                    print "Error 9: La sentencia '"+codigoPython["lineaIterativa"]+"' no aparece en la funcion "+codigoPython["nombreFuncionPrincipal"]
                                    contadorEntradasBruto+=1
                                    continue
                                    
                                #Se quita el primer elemento pues es cuando entra a la iteracion (iteracion 0)
                                listaTrazasLineaIterativa=listaTrazasLineaIterativa[1:]
                                cantidadLineasTrazaIterativa=len(listaTrazasLineaIterativa)
                                
                                #esta cantidad no sirve para generar alternativas distractoras fiables
                                #este criterio me asegura generar alternativas con una vecindad de -2 y +2
                                if cantidadLineasTrazaIterativa==0 or cantidadLineasTrazaIterativa+2<xmlEntradaObject.cantidadAlternativas:
                                    print "Error: La entrada '"+codigoPython["entradasBruto"][contadorEntradasBruto]+"' genera "+str(cantidadLineasTrazaIterativa)+" iteraciones. Cantidad Insuficiente para generar preguntas de "+str(xmlEntradaObject.cantidadAlternativas) +" alternativas"
                                    contadorEntradasBruto+=1
                                    continue
                                
                                alternativaCorrecta=copy.copy(listaTrazasLineaIterativa[-1])
                                pozoDistractores=generaPozoAlternativas(alternativaCorrecta)
                                
                                alternativaCorrecta=generaAlternativaCorrecta(alternativaCorrecta,xmlEntradaObject.puntaje)
                                
                                borraHijos(subRaizSalida)
                                seccionCodigo=ET.SubElement(subRaizSalida,'codigoPython')
                                seccionCodigo.text=codigoPython["codigoBruto"]
                                seccionAlternativas=ET.SubElement(subRaizSalida,'alternativas')
                                trazaIteraciones=ET.SubElement(subRaizSalida,'solucion')
                                
                                for cadaCombinacion in list(itertools.combinations(pozoDistractores,int(xmlEntradaObject.cantidadAlternativas)-1)):
                                    contador+=1
#                                   #menciona las iteraciones de cada alternativa separados por una +
                                    numerosIteracion=""
                                    for distractor in cadaCombinacion:
#                                     #se agrega al pozo de alternativas con algun identificador, identificando que son distractores y senalando tambien en el root de la alternativas, con que entrada y que funcion fue hecha
                                        numerosIteracion+=agregaAlternativaIteracion(seccionAlternativas,distractor)+"+"
                                    numerosIteracion+=agregaAlternativaIteracion(seccionAlternativas,alternativaCorrecta)+"+"
                                    idXmlSalida=incluyeInfo(codigoPython,trazaIteraciones,seccionAlternativas,plantillaSalida,contadorEntradasBruto,copy.copy(enunciado),numerosIteracion.rstrip("+"),listaTrazasLineaIterativa[:])
                                    
                                    if banderaEstado==True:
                                        #print ET.tostring(plantillaSalida, 'utf-8', method="xml")
                            
                                        xmlSalida.escribePlantilla(kwuargs['directorioSalida'],xmlEntradaObject.tipo,idXmlSalida,copy.copy(plantillaSalida),'xml')       
                                        borraHijos(seccionAlternativas)                               

                            #La bandera se setea a False por cada archivo temporal que se comprueba
                            banderaEstado=False
                            contadorEntradasBruto+=1
    print xmlEntradaObject.idOrigenEntrada+"->"+str(contador)+' Creados'                         
    pass

# Declaracion de directorio de entradas
nombreDirectorioEntradas="./Entradas"
nombreDirectorioPlantillas="./Plantillas"
nombreDirectorioSalidas="Salidas"
nombreCompilador="python"
tipoPregunta='pythonIterativoInvertido'
listaXmlEntrada=list()

if nombres.validaExistenciaArchivo(nombreDirectorioEntradas)==True:
    listaXmlEntrada=xmlSalida.lecturaXmls(nombreDirectorioEntradas, tipoPregunta)

for cadaXmlEntrada in listaXmlEntrada:
    retornaPlantilla(nombreDirectorioPlantillas, cadaXmlEntrada, cadaXmlEntrada.cantidadAlternativas,tipoPregunta, directorioSalida=nombreDirectorioSalidas+'/'+tipoPregunta)