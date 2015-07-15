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

import clases.alternativa as alternativa
import clases.xmlEntrada as xmlEntrada
import nombres, acceso, sys,hashlib, argparse, copy
from xml.dom import minidom

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    
def plantillaGenericaSalida():
    #info='<?xml version="1.0" encoding="UTF-8"?>\n<?xml-stylesheet href="salida.css" title="Estilo Estandar"?>'
    #ET.SubElement(tree,'plantilla')
    raizXml=ET.Element('plantilla')
    ET.SubElement(raizXml,'enunciado')
    ET.SubElement(raizXml,'opciones')
    return raizXml

def incluyeAlternativas(elementTreeObject,xmlEntradaObject):
    for subRaiz in elementTreeObject.iter():
        if subRaiz.tag=='opciones':
            del subRaiz
    opciones=ET.SubElement(elementTreeObject, 'opciones')
    for conjuntoAlternativas in xmlEntradaObject.permutaAlternativas():
        for alternativa in conjuntoAlternativas:
            opcion = ET.SubElement(opciones, 'alternativa',puntaje=alternativa.puntaje,id=alternativa.llave,tipo=alternativa.tipo)
            opcion.text=alternativa.glosa
            hijo=ET.SubElement(opcion, 'comentario')
            hijo.text=alternativa.comentario
        print ET.tostring(elementTreeObject, 'utf-8', method="xml")

def agregaAlternativa(listaAlternativas,alternativaAAgregar,largoMax):
    if len(listaAlternativas)==largoMax:
        return 0
    for alternativa in listaAlternativas:
        if alternativa.llave==alternativaAAgregar.llave:
            return False
    listaAlternativas.append(alternativaAAgregar)
    return True

def despejaAlternativas(conjuntoAlternativas):
    listaLlaves=list()
    for alternativa in conjuntoAlternativas:
        if alternativa.llave in listaLlaves:
            return False
        else:
            listaLlaves.append(alternativa.llave)
    return True

def validaConjuntoAlternativas(conjuntoAlternativas):
    indicaExistenciaRespuesta=False
    for alternativa in conjuntoAlternativas:
        if alternativa.tipo=='solucion':
            indicaExistenciaRespuesta=True
    if indicaExistenciaRespuesta==True:
        return True
    else:
        return False

def analizadorComparacion(raizXmlEntrada):
    contadorIDprovisorio=0
    archivo=open("Modulos/v1/traceFuntions.py", "r")
    funcionTracer = archivo.read()
    archivo.close()
    archivo=open("Modulos/v1/testEstandar.py", "r+")
    testEstandar=list()
    for linea in archivo:
        testEstandar.append(linea)
    archivo.close()
    listaCodigos=[]
    listaEntradas=[]
    comentarios=[]
    listaIDOcupadas=[]
    for subRaiz in raizXmlEntrada.iter("codigo"):
        for seccion in subRaiz:
            #Cada codigo incrustado y su informacion se agrega a la listaCodigos
            if seccion.tag=='python':
                codigo={}
                try:
                    if not seccion.attrib['id'] in listaIDOcupadas:
                        codigo["id"]=seccion.attrib['id']
                        listaIDOcupadas.append(codigo["id"])
                    else:
                        temp=""
                        codigo["id"]=seccion.attrib['id']
                        while codigo["id"] in listaIDOcupadas:
                            temp=codigo["id"]
                            codigo["id"]="D_"+codigo["id"]
                        print "Precaucion 4: La id '"+temp+"' ya esta ocupada y se ha asignado ID="+codigo["id"]                    
                        listaIDOcupadas.append(codigo["id"])
                except:
                    codigo["id"]="null_"+str(contadorIDprovisorio)
                    print "Precaucion 3: un codigo carece de Id y se ha asignado ID="+codigo["id"]
                    listaIDOcupadas.append(codigo["id"])
                    contadorIDprovisorio+=1
                codigo["codigoBruto"]=seccion.text.rstrip().lstrip()
                for subSeccion in seccion:
                    if subSeccion.tag=='nombreFuncionPrincipal':
                        codigo["nombreFuncionPrincipal"]=subSeccion.text.rstrip().lstrip()
                listaCodigos.append(codigo)
            #Cada entrada para los codigos y agrega a la listaDeEntradas
            if seccion.tag=='entrada':
                entrada={}
                entrada["entradaBruta"]=seccion.text.rstrip().lstrip()
                listaValores=[]
                for entradaTemp in entrada["entradaBruta"].split(';'):
                    listaValores.append(entradaTemp.split('=')[-1])
                listaValores=','.join(listaValores)
                entrada["entrada"]=listaValores
                listaEntradas.append(entrada)
            #Se anidan los comentarios en uno solo
            if seccion.tag=='comentario':
                comentarios.append(seccion.text.rstrip().lstrip())
    comentarios='\n'.join(comentarios)
    listaCodigosPorEntrada=[]
    #Luego para cada entrada
    codigo={}
    for codigoPorEntrada in listaEntradas:
        codigoPorEntrada["codigos"]=[]
        codigo["funcionEntrada"]=""
        #Se genera un archivo temporal con cada codigo y la entrada actual
        for codigo in listaCodigos:
            try:
                codigoPorEntrada["funcionEntrada"]=codigo["nombreFuncionPrincipal"]+'('+codigoPorEntrada["entrada"]+')'
            except:
                print "Error 6: una o mas funciones no especifican el nombre de su funcion principal"
                exit()
            #El siguiente print muestra las funciones evaluadas disponibles por entrada y codigo
            #print codigoPorEntrada["funcionEntrada"]
            codigo["codigo"]=acceso.make_tempPython2(codigo["codigoBruto"], funcionTracer, testEstandar,codigoPorEntrada["funcionEntrada"][:])
            codigoPorEntrada["codigos"].append(copy.copy(codigo))
        #Resultando en un codigoPorEntrada de la forma {entradaActual:Lista de archivos temporales con la entrada actual evaluada}
        listaCodigosPorEntrada.append(codigoPorEntrada)
    #print listaCodigosPorEntrada
    return listaCodigosPorEntrada, comentarios

def analizadorIteracion(raizXmlEntrada):
    contadorIDprovisorio=0
    listaIDOcupadas=[]
    listaCodigosPython=list()
    archivo=open("Modulos/v1/traceFuntions.py", "r")
    funcionTracer = archivo.read()
    archivo.close()
    archivo=open("Modulos/v1/testEstandar.py", "r+")
    testEstandar=list()
    for linea in archivo:
        testEstandar.append(linea)
    #testEstandar = archivo.read()
    archivo.close()
    #aqui se crea el trazador de funciones en el mismo directorio temporal en donde se
    #pondran las demas funciones python
    #archivoTracer=acceso.make_traceFuntionsFile(contenido)
    for subRaiz in raizXmlEntrada.iter("codigo"):
        for codigoPython in subRaiz:
            if codigoPython.tag=='python':
                dicCodigoPython=dict()
                dicCodigoPython["cantidadCiclosConsulta"]=list()
                try:
                    if not codigoPython.attrib["id"] in listaIDOcupadas:
                        dicCodigoPython["id"]=codigoPython.attrib['id']
                        listaIDOcupadas.append(dicCodigoPython["id"])
                    else:
                        temp=""
                        dicCodigoPython["id"]=codigoPython.attrib['id']
                        while dicCodigoPython["id"] in listaIDOcupadas:
                            temp=dicCodigoPython["id"]
                            dicCodigoPython["id"]="D_"+dicCodigoPython["id"]
                        print "Precaucion 4: La id '"+temp+"' ya esta ocupada y se ha asignado ID="+dicCodigoPython["id"]
                        listaIDOcupadas.append(dicCodigoPython["id"])   
                except:
                    dicCodigoPython["id"]="null_"+str(contadorIDprovisorio)
                    print "Precaucion 3: un codigo carece de Id y se ha asignado ID="+dicCodigoPython["id"]
                    listaIDOcupadas.append(dicCodigoPython["id"])
                    contadorIDprovisorio+=1
                dicCodigoPython["entradas"]=list()
                dicCodigoPython["entradasBruto"]=list()
                comentariosCodigo=""
                dicCodigoPython["cantidadCiclosConsulta"]=list()
                for subRaizCodigo in codigoPython:
                    if subRaizCodigo.tag=='nombreFuncionPrincipal':
                        dicCodigoPython["nombreFuncionPrincipal"]=subRaizCodigo.text.rstrip().lstrip()
                    elif subRaizCodigo.tag=='entrada':
                        dicCodigoPython["entradasBruto"].append(subRaizCodigo.text.rstrip().lstrip())
                        listaValores=list()
                        try:
                            entradaParseada=subRaizCodigo.text.split(';')
                        except:
                            print "Error 10: Una o mas entradas son invalidas en una de las entradas de la funciones Python adjuntas"
                            entradaParseada=""
                        for entradaTemp in entradaParseada:
                            listaValores.append(entradaTemp.split('=')[-1])
                        listaValores=','.join(listaValores)
                        dicCodigoPython["entradas"].append(listaValores)
                #No se valida si es numero la entrada
                    elif subRaizCodigo.tag=='cantidadCiclosConsulta':
                        dicCodigoPython["cantidadCiclosConsulta"].append(subRaizCodigo.text.rstrip().lstrip())
                    elif subRaizCodigo.tag=='lineaIterativa':
                        dicCodigoPython["lineaIterativa"]=subRaizCodigo.text.rstrip().lstrip()
                    elif subRaizCodigo.tag=='comentario':
                        comentariosCodigo=comentariosCodigo+" "+subRaizCodigo.text.rstrip().lstrip()
                stringFuncionEntrada=list()
                dicCodigoPython["codigo"]=list()
                for entrada in dicCodigoPython["entradas"]:
                    try:
                        funcionEntrada=dicCodigoPython["nombreFuncionPrincipal"]+'('+entrada+')'
                    except:
                        print "Error 6: una o mas funciones no especifican el nombre de su funcion principal"
                        exit()
                    stringFuncionEntrada.append(funcionEntrada)
                    codigoPyConEntrada=acceso.make_tempPython2(codigoPython.text.rstrip().lstrip(), funcionTracer, testEstandar, funcionEntrada)
                    dicCodigoPython["codigo"].append(codigoPyConEntrada)
                dicCodigoPython["codigoBruto"]=codigoPython.text.rstrip().lstrip()
                if len(str(dicCodigoPython["codigoBruto"]))<5:
                    print "Error 12: Una o mas entradas no contienen codigo python adjunto y se han omitido"
                    continue
                dicCodigoPython["comentarios"]=comentariosCodigo
                #Lista de diccionarios que contiene info del codigo python incrustado
                #cada diccionario contiene:
                #"codigo": archivo temporal con codigo python,
                #"entrada": lista con las entradas que se quieren ingresar al codigo
                #"comentario": string que tiene concatenado todos los comentarios
                #print dicCodigoPython
                listaCodigosPython.append(dicCodigoPython)
    #Para eliminar el archivo temporal
    #os.unlink(dicCodigoPython["codigo"].name) 
    return listaCodigosPython

def analizadorTraza(raizXmlEntrada):
    listaCodigosPython=list()
    archivo=open("Modulos/v1/traceFuntions.py", "r")
    funcionTracer = archivo.read()
    archivo.close()
    archivo=open("Modulos/v1/testEstandar.py", "r+")
    testEstandar=list()
    for linea in archivo:
        testEstandar.append(linea)
    #testEstandar = archivo.read()
    archivo.close()
    #aqui se crea el trazador de funciones en el mismo directorio temporal en donde se
    #pondran las demas funciones python
    #archivoTracer=acceso.make_traceFuntionsFile(contenido)
    contadorIDprovisorio=0
    listaIDOcupadas=[]
    for subRaiz in raizXmlEntrada.iter("codigo"):
        for codigoPython in subRaiz:
            dicCodigoPython=dict()
            if codigoPython.tag=='python':
                try:
                    if not codigoPython.attrib['id'] in listaIDOcupadas:
                        dicCodigoPython["id"]=codigoPython.attrib['id']
                        listaIDOcupadas.append(dicCodigoPython["id"])
                    else:
                        temp=""
                        dicCodigoPython["id"]=codigoPython.attrib['id']
                        while dicCodigoPython["id"] in listaIDOcupadas:
                            temp=dicCodigoPython["id"]
                            dicCodigoPython["id"]="D_"+dicCodigoPython["id"]
                        print "Precaucion 4: La id '"+temp+"' ya esta ocupada y se ha asignado ID="+dicCodigoPython["id"]                    
                        listaIDOcupadas.append(dicCodigoPython["id"])
                except:
                    dicCodigoPython["id"]="null_"+str(contadorIDprovisorio)
                    print "Precaucion 3: un codigo carece de Id y se ha asignado ID="+dicCodigoPython["id"]
                    listaIDOcupadas.append(dicCodigoPython["id"])
                    contadorIDprovisorio+=1                  
            dicCodigoPython["entradas"]=list()
            dicCodigoPython["entradasBruto"]=list()
            comentariosCodigo=""
            for subRaizCodigo in codigoPython:
                if subRaizCodigo.tag=='nombreFuncionPrincipal':
                    dicCodigoPython["nombreFuncionPrincipal"]=subRaizCodigo.text.rstrip().lstrip()
                elif subRaizCodigo.tag=='entrada':
                    listaValores=list()
                    try:
                        desgloseEntrada=subRaizCodigo.text.split(';')
                        dicCodigoPython["entradasBruto"].append(subRaizCodigo.text.rstrip().lstrip())
                    except:
                        print "Error 11: La entrada: 'None' presenta una falla y no se puede Trazar"
                        continue
                    for entradaTemp in desgloseEntrada:
                        listaValores.append(entradaTemp.split('=')[-1])
                    listaValores=','.join(listaValores)
                    dicCodigoPython["entradas"].append(listaValores)
                elif subRaizCodigo.tag=='comentario':
                    comentariosCodigo=comentariosCodigo+" "+subRaizCodigo.text.rstrip().lstrip()
            stringFuncionEntrada=list()
            dicCodigoPython["codigo"]=list()
            for entrada in dicCodigoPython["entradas"]:
                try:
                    funcionEntrada=dicCodigoPython["nombreFuncionPrincipal"]+'('+entrada+')'
                except:
                    print "Error 6: una o mas funciones no especifican el nombre de su funcion principal"
                    continue
                stringFuncionEntrada.append(funcionEntrada)
                codigoPyConEntrada=acceso.make_tempPython2(codigoPython.text.rstrip().lstrip(), funcionTracer, testEstandar, funcionEntrada)
                dicCodigoPython["codigo"].append(codigoPyConEntrada)
            dicCodigoPython["codigoBruto"]=codigoPython.text.rstrip().lstrip()
            dicCodigoPython["comentarios"]=comentariosCodigo
            #Lista de diccionarios que contiene info del codigo python incrustado
            #cada diccionario contiene:
            #"codigo": archivo temporal con codigo python,
            #"entrada": lista con las entradas que se quieren ingresar al codigo
            #"comentario": string que tiene concatenado todos los comentarios
            listaCodigosPython.append(dicCodigoPython)
    return listaCodigosPython

def analizadorEnunciadoIncompleto(raizXmlEntrada):
    pass

def preguntaParser(raizXmlEntrada,nombreArchivo):
    puntaje=0
    tipo=""
    cantidadAlternativas=0
    conjuntoAlternativas=dict()
    comentarioAlternativa=""
    termino="" #Para el tipo pregunta definicion
    enunciado="" #Para el tipo pregunta enunciadoIncompleto
    for subRaiz in raizXmlEntrada.iter('pregunta'):
        try:
            puntaje=int((subRaiz.attrib['puntaje']))
        except:
            puntaje=2
        tipo=str(subRaiz.attrib['tipo'])
        try:
            cantidadAlternativas=int(subRaiz.attrib['cantidadAlternativas'])
        except:
            cantidadAlternativas=4
        try:
            idOrigenEntrada=str(subRaiz.attrib['idOrigenEntrada'])
        except:
            print "Precaucion 1: el atributo 'idOrigenEntrada' no existe en el documento '"+nombreArchivo+"'.\nY se ha asignado idOrigenEntrada=null"
            idOrigenEntrada="null"
        
    if tipo=='definicion':
        for subRaiz in raizXmlEntrada.iter('termino'):
            termino=subRaiz.text.rstrip().lstrip()
    elif tipo=='pythonCompara':
        listaCodigosPorEntrada, comentarios=analizadorComparacion(raizXmlEntrada)
        return xmlEntrada.xmlEntrada(nombreArchivo,tipo,puntaje,conjuntoAlternativas,cantidadAlternativas,codigos=listaCodigosPorEntrada,comentarios=comentarios,idOrigenEntrada=idOrigenEntrada)

    elif tipo=='pythonIterativo' or tipo=='pythonIterativoInvertido':
        listaCodigosPython=analizadorIteracion(raizXmlEntrada)
        return xmlEntrada.xmlEntrada(nombreArchivo,tipo,puntaje,conjuntoAlternativas,cantidadAlternativas,codigos=listaCodigosPython,idOrigenEntrada=idOrigenEntrada)

    elif tipo=='pythonTraza':
        listaCodigosPython=analizadorTraza(raizXmlEntrada)
        return xmlEntrada.xmlEntrada(nombreArchivo,tipo,puntaje,conjuntoAlternativas,cantidadAlternativas,codigos=listaCodigosPython,idOrigenEntrada=idOrigenEntrada)

    elif tipo=='enunciadoIncompleto':
        respuestas=list()
        presenciaBlank=False
        enunciadoIncompleto=list()
        for subRaiz in raizXmlEntrada.iter('enunciado'):
            for elem in subRaiz:
                if elem.tag=='glosa':
                    enunciadoIncompleto.append(elem.text.rstrip().lstrip())
                if elem.tag=='blank':
                    enunciadoIncompleto.append('_'*len(elem.text.rstrip().lstrip()))
                    respuestas.append(elem.text.rstrip().lstrip())
                    presenciaBlank=True
        if presenciaBlank==False:
            print "Error 3: El documento '"+nombreArchivo+"' no presenta terminos en el tag 'blank' que representan las alternativas solucion del item"
            exit()
        enunciado=' '.join(enunciadoIncompleto)
        alternativaSolucion=list()
        alternativaSolucion.append(alternativa.alternativa(hashlib.sha256('solucion').hexdigest(),'solucion',str(puntaje),'-'.join(respuestas),comentario='Alternativa Correcta',numeracion=1))
        conjuntoAlternativas[alternativaSolucion[0].llave]=alternativaSolucion
    elif tipo=='definicionPareada':
        #Valores por default
        composicionDistractores="1+2"
        criterioOrdenDistractores="None"
        ordenTerminos="None"
        cantidadCombinacionesDefiniciones=1
        #Se obtienen especificaciones para formar los distractores
        for subRaiz in raizXmlEntrada.iter('pregunta'):
            try:
                if bool(str(subRaiz.attrib['composicionDistractores']).rstrip())==True:
                    composicionDistractores=str(subRaiz.attrib['composicionDistractores'])
                if bool(str(subRaiz.attrib['ordenDistractores']).rstrip())==True:
                    criterioOrdenDistractores=str(subRaiz.attrib['ordenDistractores'])
                if bool(str(subRaiz.attrib['ordenTerminos']).rstrip())==True:
                    ordenTerminos=str(subRaiz.attrib['ordenTerminos'])
                if bool(str(subRaiz.attrib['cantidadCombinacionesDefiniciones']).rstrip())==True:
                    cantidadCombinacionesDefiniciones=int(subRaiz.attrib['cantidadCombinacionesDefiniciones'])
            except:
                #valor por defecto "1+2"
                pass
            #Si existe el atributo en la entrada xml
        conjuntoTerminosPareados={}
        conjuntoTerminosImpares={}
        ##validar que la id no haya sido procesada con anterioridad
        listaIDs=[]
        for subRaiz in raizXmlEntrada.iter('definiciones'):
            for glosa in subRaiz.iter('glosa'):
                definicion=glosa.text.rstrip().lstrip()
                llaveTermino=glosa.attrib['id']
                if llaveTermino in listaIDs:
                    continue
                else:
                    listaIDs.append(llaveTermino)
                pozoPares=[]
                pozoImpares=[]
                for par in glosa.iter('par'):
                    pozoPares.append(alternativa.alternativa(llaveTermino,'solucion',str(puntaje),par.text.rstrip()))
                for inpar in glosa.iter('inpar'):
                    textoComentario=""
                    for comentario in inpar.iter('comentario'):
                        textoComentario=textoComentario+' '+comentario.text.rstrip().lstrip()
                    #textoComentario=textoComentario.lstrip()
                    #agrego solo si existe el inpar
                    if bool(inpar.text.rstrip())==True:
                        pozoImpares.append(alternativa.alternativa(llaveTermino,'distractor','0',inpar.text.rstrip(),comentario=textoComentario.rstrip()))
                conjuntoTerminosPareados[definicion.rstrip()]=pozoPares
                #No es necesario agregar una llave si no tiene impares
                if len(pozoImpares)>0:
                    conjuntoTerminosImpares[definicion.rstrip()]=pozoImpares
            conjuntoAlternativas['terminos']=conjuntoTerminosPareados
            conjuntoAlternativas['distractores']=conjuntoTerminosImpares
        #Se puede retornar antes el de definicion pareada, pues no presenta seccion opciones, sino una seccion completa de definiciones con sus pares e impares
        #Ademas este tipo de pregunta tiene mas atributos
        return xmlEntrada.xmlEntrada(nombreArchivo,tipo,puntaje,conjuntoAlternativas,cantidadAlternativas,termino=termino,enunciado=enunciado,composicionDistractores=composicionDistractores,criterioOrdenDistractores=criterioOrdenDistractores,ordenTerminos=ordenTerminos,cantidadCombinacionesDefiniciones=cantidadCombinacionesDefiniciones, idOrigenEntrada=idOrigenEntrada)
            #print conjuntoAlternativas['terminos'].keys()
    #En la pregunta tipo definicion pareada la arquitectura del conjunto de alternativas cambia
    #ahora es {'terminos':{'definicion':lista de alternativas (las diferentes definiciones)}}
    #{'distractores':{'definicion':lista de distractores (los diferentes distractores)}}
    for subRaiz in raizXmlEntrada.iter('opciones'):
        for opcion in raizXmlEntrada.iter('alternativa'):
            try:
                idAlternativa=opcion.attrib['id']
            except:
                print "Precaucion 2: una alternativa carece de Id y se ha omitido"
                continue
            try:
                tipoOpcion=opcion.attrib['tipo']
                print tipoOpcion
                if not(tipoOpcion is 'solucion' or "distractor"):
                    print "Error1: El atributo tipo contiene un nombre distinto de 'solucion' o 'distractor'"
                    continue
            except:
                    print "Error1: El atributo tipo contiene un nombre distinto de 'solucion' o 'distractor'"
                    continue
                       
            for glosaOpcion in opcion.iter('glosa'):
                comentarioAlternativa=""
                for comentarioGlosa in glosaOpcion.iter('comentario'):
                    comentarioAlternativa=comentarioAlternativa+" "+str(comentarioGlosa.text).rstrip().lstrip()
#                 try:
#                     idAlternativa=opcion.attrib['id']
#                 except:
#                     print "Precaucion 2: una alternativa carece de Id y se ha omitido"
#                     continue
                if idAlternativa in conjuntoAlternativas.keys():
                    largoLista=len(conjuntoAlternativas[opcion.attrib['id']])
                    if tipoOpcion=="solucion":
                        conjuntoAlternativas[opcion.attrib['id']].append(alternativa.alternativa(opcion.attrib['id'],opcion.attrib['tipo'],str(puntaje),glosaOpcion.text.rstrip(),comentario=comentarioAlternativa,numeracion=largoLista+1))
                    else:
                        conjuntoAlternativas[opcion.attrib['id']].append(alternativa.alternativa(opcion.attrib['id'],opcion.attrib['tipo'],str(0),glosaOpcion.text.rstrip(),comentario=comentarioAlternativa,numeracion=largoLista+1))
                else:
                    conjuntoAlternativas[opcion.attrib['id']]=list()
                    try:
                        if opcion.attrib['tipo']=="solucion":
                            conjuntoAlternativas[opcion.attrib['id']].append(alternativa.alternativa(opcion.attrib['id'],opcion.attrib['tipo'],str(puntaje),glosaOpcion.text.rstrip(),comentario=comentarioAlternativa,numeracion=1))
                        else:
                            conjuntoAlternativas[opcion.attrib['id']].append(alternativa.alternativa(opcion.attrib['id'],opcion.attrib['tipo'],str(0),glosaOpcion.text.rstrip(),comentario=comentarioAlternativa,numeracion=1)) 
                    except:
                        print "Error1: El atributo tipo contiene un nombre distinto de 'solucion' o 'distractor'"
                        exit()                    
    return xmlEntrada.xmlEntrada(nombreArchivo,tipo,puntaje,conjuntoAlternativas,cantidadAlternativas,termino=termino,enunciado=enunciado, idOrigenEntrada=idOrigenEntrada)

#Funcion que analiza argumentos ingresados por comando al ejecutar la funcion
#Retorna la cantidad de alternativas ingresada por el usuario, en caso que no
#se detecte numero alguno ingresado, retorna valor por defecto que es 4
def argParse():
    parser = argparse.ArgumentParser(description='Cantidad de alternativas presentes al momento de generar las preguntas')
    parser.add_argument('-c', required=False,type=int, default=4,
                    help='Especifica la cantidad de alternativas',
                    metavar="CantidadDeAlternativas")
    return parser.parse_args().c

def incrustaAlternativasXml(subRaizOpciones,listaAlternativas):
    #Se concatena el texto de todas las alternativas
    glosasAlternativas=""
    identificadorPregunta=""
    for elem in subRaizOpciones.getchildren():
        subRaizOpciones.remove(elem)
    for alternativa in listaAlternativas:
        identificadorPregunta+=alternativa.identificador()
        opcion = ET.SubElement(subRaizOpciones, 'alternativa')
        opcion.text=alternativa.glosa
        glosasAlternativas+=alternativa.glosa
        opcion.set('puntaje',alternativa.puntaje)
        opcion.set('id',alternativa.llave)
        opcion.set('tipo',alternativa.tipo)
        hijo=ET.SubElement(opcion, 'comentario')
        hijo.text=alternativa.comentario
    #A partir del texto concatenado, se crea una unica ID que representa las alternativas
    #Esta ID se asigna a un nuevo atributo a la subRaiz 'opciones'
    idItem=hashlib.sha256(glosasAlternativas).hexdigest()
    subRaizOpciones.set('id',idItem)
    subRaizOpciones.set('idPreguntaGenerada',identificadorPregunta.rstrip())
    return idItem,identificadorPregunta.rstrip()

#Funcion que analiza cada Xml de entrada
#Si este es de un cierto tipo indicado por la entrada, se parsea con la funcion
#preguntaParser y se agrega a una lista de xmlsFormateadas
#Finalmente retorna esta lista
def lecturaXmls(nombreDirectorioEntradas,tipo):
    listaXmlFormateadas=list()
    for xmlEntrada in nombres.fullEspecificDirectoryNamesXML(nombreDirectorioEntradas):
        try:
            arbolXml = ET.ElementTree(file=xmlEntrada)
            raizXml=arbolXml.getroot()
        except Exception,e:
            #e = sys.exc_info()[0]
            print "Error 2: El documento '"+xmlEntrada+"' presenta una falla en"+str(e).split(":")[1]
            continue
            #exit()
        if raizXml.attrib['tipo']==tipo: #'definicion':
            listaXmlFormateadas.append(preguntaParser(raizXml,nombres.obtieneNombreArchivo(xmlEntrada)))
    return listaXmlFormateadas

def _xmlprettyprint(stringlist):
    indent = ' '
    in_tag = False
    for token in stringlist:
        if token.startswith('</'):
            indent = indent[:-2]
            yield indent + token + '\n'
            in_tag = True
        elif token.startswith('<'):
            yield indent + token
            indent += '  '
            in_tag = True
        elif token == '>':
            yield '>' + '\n'
            in_tag = False
        elif in_tag:
            yield token
        else:
            yield token
 
 
def xmlprettyprint(element):
    return ''.join(_xmlprettyprint(ET.tostringlist(element,'utf-8')))

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent=" ")

def escribePlantilla(directorioSalida,tipoPregunta,nombreArchivo,raizXML,formato):
    acceso.CrearDirectorio(directorioSalida+'/'+tipoPregunta)
    tree = ET.ElementTree(raizXML)
    
    DECLARATION = """<?xml version="1.0" encoding="utf-8"?>\n<?xml-stylesheet href="../../css/salida.css" title="Estilo Estandar"?>\n"""
    
    #tree = ET.parse(filename)
    # do some work on tree
    
    with open(directorioSalida+'/'+nombreArchivo+'.'+formato, 'w') as output: # would be better to write to temp file and rename
        output.write(DECLARATION)
        output.write(xmlprettyprint(raizXML))
        #output.write(ET.tostring(raizXML, 'utf-8', method="xml"))
        #tree.write(output, xml_declaration=False, encoding='utf-8') 
    # xml_declaration=False - don't write default declaration
    
    #tree.write(directorioSalida+'/'+nombreArchivo+'.'+formato, encoding='UTF-8', xml_declaration=False)
    #pass

def escribePlantilla2(directorioSalida,tipoPregunta,nombreArchivo,raizXML,formato):
    acceso.CrearDirectorio(directorioSalida+'/'+tipoPregunta)
    tree = ET.ElementTree(raizXML)
    
    DECLARATION = """<?xml version="1.0" encoding="utf-8"?>\n<?xml-stylesheet href="../../css/salida.css" title="Estilo Estandar"?>\n"""
    
    #tree = ET.parse(filename)
    # do some work on tree
    
    with open(directorioSalida+'/'+nombreArchivo+'.'+formato, 'w') as output: # would be better to write to temp file and rename
        output.write(DECLARATION)
       # output.write(xmlprettyprint(raizXML))
        output.write(ET.tostring(raizXML, 'utf-8', method="xml"))
        #tree.write(output, xml_declaration=False, encoding='utf-8')
    pass 