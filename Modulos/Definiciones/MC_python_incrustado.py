'''
Created on 16-04-2015

@author: Marcial
'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import sys
import nombres, xmlSalida, acceso, ast,json
import plantilla
from matplotlib.cbook import Null
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import subprocess

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
            linea="Linea:"+str(linea["numLinea"])+': '+linea["linea"]+" - Stack: "+stack+" - Funcion de procedencia: "+linea['funcionProcedencia']
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
                    linea["varLocales"]=ast.literal_eval(linea["varLocales"]) #listo!
                    linea["varGlobales"]=ast.literal_eval(linea["varGlobales"])
                    linea["argumentos"]=ast.literal_eval(linea["argumentos"])
                    if "_run_exitfuncs" in linea["funcionProcedencia"]:
                        banderaAgregaLinea=False
                    #print type(linea["argumentos"])
                elif linea["evento"]=='return':
                    linea["retorno"]=ast.literal_eval(linea["retorno"])
                    if "_run_exitfuncs" in linea["funcionProcedencia"]:
                        banderaAgregaLinea=False
                elif linea["evento"]=='call':
                    if "_run_exitfuncs" in linea["invocacion"] or "_remove" in linea["invocacion"]:
                        banderaAgregaLinea=False
            if banderaAgregaLinea==True:
                listaLineasTraza.append(linea)
    return listaLineasTraza

#Funcion que analiza la plantilla que corresponde a este tipo de pregunta
#A esa plantilla se le anaden los datos obtenidos desde la entrada de
#su mismo tipo, luego una vez completada la pregunta, se imprime
#por pantalla para que la informacion pueda ser recogida por el programa
#principal

def recogePlantillas(nombreDirectorioPlantillas,tipoPregunta):
    validaPlantilla=False
    plantillasValidas=list()
    for archivoPlantilla in nombres.especificDirectoryNames(nombreDirectorioPlantillas):
        nombreDirectorioArchivoPlantilla=nombres.directorioReal(nombreDirectorioPlantillas+"/"+archivoPlantilla)
        arbolXmlPlantillaEntrada = ET.ElementTree() # instantiate an object of *class* `ElementTree`
        arbolXmlPlantillaEntrada.parse(nombreDirectorioArchivoPlantilla)
        #arbolXml=ET.ElementTree(file=nombreDirectorioArchivoPlantilla)
        for subRaiz in arbolXmlPlantillaEntrada.iter('plantilla'):
            if subRaiz.attrib['tipo']==tipoPregunta:
                validaPlantilla=True
                     
        if validaPlantilla==True:
            enunciado=""
            for subRaiz in arbolXmlPlantillaEntrada.iter():
                if subRaiz.tag=='glosa':
                    enunciado=enunciado+subRaiz.text
                if subRaiz.tag=='termino':
                    enunciado=enunciado+' @termino'
            #plantillasValidas.append(arbolXmlPlantillaEntrada)
            plantillasValidas.append(plantilla.plantilla(tipoPregunta,enunciado.rstrip()))
    return plantillasValidas

def retornaPlantilla(nombreDirectorioPlantillas,xmlEntradaObject,cantidadAlternativas, tipoPregunta, **kwuargs): #,xmlEntradaObject):
    #tipoPregunta=nombres.nombreScript(__file__)
    contador=0
    idProvisorio=0
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
                if subRaizSalida.tag=='enunciado':
                    subRaizSalida.text=plantilla.enunciado
                if subRaizSalida.tag=='opciones':
                    for codigoPython in xmlEntradaObject.codigos:
                        #Por cada ciclo debo eliminar los hijos de la seccion y poner los nuevos
                        for elem in subRaizSalida.getchildren():
                            subRaizSalida.remove(elem)
                        seccionCodigo=ET.SubElement(subRaizSalida,'codigoPython')
                        seccionCodigo.text=codigoPython["codigoBruto"]
                        seccionTrazaSolucion=ET.SubElement(subRaizSalida,'trazaSolucion')
                        #lista de archivos temporales por entrada anidada al codigo
                        for archivoTemporal in codigoPython["codigo"]:
                            nombreTemporal=archivoTemporal.name
                            directorioTemporal=nombreTemporal.split("/")
                            directorioTemporal.pop()
                            directorioTemporal='/'.join(directorioTemporal)
                            directorioTemporal=nombres.directorioReal(directorioTemporal)
                            p = subprocess.Popen(["python",nombreTemporal],stdout=subprocess.PIPE, cwd=directorioTemporal)
                            streamTraza= str(p.communicate()[0]) #obtiene solo los resultados y no los errores 
                            streamTraza=obtieneTraza(streamTraza)
                            normalizaLineas(streamTraza)#Normaliza numero de lineas
                            streamTraza=estandarizaLineas(streamTraza)#Pasa las lineas a formato String
                            streamTraza=mergeLineas(streamTraza)#Pasa la lista de lineas a solo un string
                            seccionTrazaSolucion.text=streamTraza
                            if banderaEstado==True:
                                xmlSalida.escribePlantilla(kwuargs['directorioSalida'],xmlEntradaObject.tipo,str(idProvisorio),plantillaSalida,'xml')
                                idProvisorio+=1
                            else:
                                print ET.tostring(plantillaSalida, 'utf-8', method="xml")
                                idProvisorio+=1
    if banderaEstado==True:
        print str(idProvisorio)+' Creados'                         
    pass

# Declaracion de directorio de entradas
nombreDirectorioEntradas="./Entradas/Definiciones"
nombreDirectorioPlantillas="./Plantillas"
nombreDirectorioSalidas="Salidas"
nombreCompilador="python"
tipoPregunta='pythonIncrustado'
listaXmlEntrada=list()

# Almacenamiento usando el parser para este tipo de pregunta

#Ahora la entrada que indica la cantidad de alternativas viene incrustada como atributo en los respectivos
#XML de entrada
#cantidadAlternativas=xmlSalida.argParse()

if nombres.validaExistenciasSubProceso(nombreDirectorioEntradas)==True:
    listaXmlEntrada=xmlSalida.lecturaXmls(nombreDirectorioEntradas, tipoPregunta)

for cadaXmlEntrada in listaXmlEntrada:
    retornaPlantilla(nombreDirectorioPlantillas, cadaXmlEntrada, cadaXmlEntrada.cantidadAlternativas,tipoPregunta, directorioSalida=nombreDirectorioSalidas+'/'+tipoPregunta)