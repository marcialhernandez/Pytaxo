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

def formateaResultado(resultado):
    resultado=resultado.split("\n")
    while "" in resultado:
        resultado.remove("")
         
    return resultado
    
def obtenerResultadosEntrada(rutaArchivo, lenguaje):
    proceso = subprocess.Popen([lenguaje, rutaArchivo],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output, errors = proceso.communicate()
    if proceso.returncode:
        try:
            raise Exception(errors)
        except Exception as falla:
            #print type(falla.args)
            #print type(falla.args[0])
            return formateaResultado(falla.args[0])
    else:
        #print output
        return formateaResultado(output)

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
                        for archivoTemporal in codigoPython["codigo"]:
                        #print codigoPython["codigo"].name
                        #nombreTemporal=codigoPython["codigo"].name
                            nombreTemporal=archivoTemporal.name
                            #archivo=open(nombreTemporal)
                            #for line in archivo:
                            #    print line
                            directorioTemporal=nombreTemporal.split("/")
                            directorioTemporal.pop()
                            directorioTemporal='/'.join(directorioTemporal)
                            directorioTemporal=nombres.directorioReal(directorioTemporal)
                            p = subprocess.Popen(["python",nombreTemporal],stdout=subprocess.PIPE, cwd=directorioTemporal)
                            streamTraza= str(p.communicate()[0]) #obtiene solo los resultados y no los errores 
                            streamTraza=obtieneTraza(streamTraza)
                            print len(streamTraza) #38 lineas con entradas correctas
#                         
                        #obtenerResultadosEntrada(codigoPython["codigo"].name, "python")
#                         proceso = subprocess.Popen(["python", codigoPython["codigo"].name],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#                         output, errors = proceso.communicate()
#                         if proceso.returncode:
#                             try:
#                                 raise Exception(errors)
#                             except Exception as falla:
#                                     #print type(falla.args)
#                                     #print type(falla.args[0])
#                                     print falla.args[0]
#                             else:
#                                 #print output
#                                 print output
                        #acceso.obtenerResultadosEntrada(codigoPython["codigo"].name, "python")
                        #archivo=open(codigoPython["codigo"].name)
                        #for line in archivo:
                        #    print line
                        #archivoTemporal=open(codigoPython["codigo"].name,'r+')
                        #archivoTemporal=open(xmlEntradaObject.traceFuntions.name,'r+')
                        #archivoTemporal=open(codigoPython["codigo"].name,'r+')
                        #for line in archivoTemporal:
                        #    print line
                        #print linecache.getline(codigoPython["codigo"], 1)
                        #if banderaEstado==True:
                        #    xmlSalida.escribePlantilla(kwuargs['directorioSalida'],xmlEntradaObject.tipo, identificadorItem+' '+identificadorAlternativas+' '+str(contador), plantillaSalida,'xml')
                        #else:
                        #    print ET.tostring(plantillaSalida, 'utf-8', method="xml")
    #if banderaEstado==True:
    #    print str(contador)+' Creados'                            
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