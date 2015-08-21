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

from clases import alternativa as ALT
import clases.xmlEntrada as xmlEntrada
import nombres, acceso, sys,hashlib, argparse, copy
from xml.dom import minidom
reload(sys)  
sys.setdefaultencoding('utf8')

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

def strToSN(v):
  if v.lower() in ["yes", "true", "t", "1","si","y","s"]:
      return "S"
  else:
      return "N"

def determinaNumerado(v):
    if v in ['none', 'abc', 'ABCD','123']:
        return "S"
    else:
        return "N"

def determinaFormatoSalida(v):
    if v.lower() in ['quiz', 'answer']:
        return "S"
    else:
        return "N"
    
def plantillaGenericaSalida(puntajeValue,shuffleanswersValue,penaltyValue,answernumberingValue):
    raizXml=ET.Element('question')
    raizXml.set('type','multichoice')
    name=ET.SubElement(raizXml,'name')
    ET.SubElement(name,'text')
    questiontext=ET.SubElement(raizXml,'questiontext')
    ET.SubElement(questiontext,'text')
    defaultgrade=ET.SubElement(raizXml,'defaultgrade')
    defaultgrade.text=str(puntajeValue)
    shuffleanswers=ET.SubElement(raizXml,'shuffleanswers') # (values: 1/0) #banderizar
    shuffleanswers.text=shuffleanswersValue
    single=ET.SubElement(raizXml,'single')
    single.text='true'
    answernumbering=ET.SubElement(raizXml,'answernumbering') #(allowed values: 'none', 'abc', 'ABCD' or '123') #banderizar
    answernumbering.text=answernumberingValue
    penalty=ET.SubElement(raizXml,'penalty')
    penalty.text=penaltyValue
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
    posiblesEntradasHidden=["si","SI","True","true","1","TRUE","Si"]
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
    for subRaiz in raizXmlEntrada.iterfind("codigo"):
        atributoHidden=False
        for codigoPython in subRaiz.iterfind("python"):
            dicCodigoPython=dict()
            dicCodigoPython["cantidadCiclosConsulta"]=list()
            ####Lo que se evalua
            dicCodigoPython["codigoBruto"]=[]
            ####Lo que se muestra
            dicCodigoPython["codigoEnunciado"]=[]
            for textoCodigo in codigoPython.iterfind("text"):
                try:
                    if textoCodigo.attrib['hidden'] in posiblesEntradasHidden:
                        atributoHidden=True
                    else:
                        atributoHidden=False
                except:
                    atributoHidden=False
                if atributoHidden==True:
                    dicCodigoPython["codigoBruto"].append(textoCodigo.text.rstrip().lstrip())
                else:
                    dicCodigoPython["codigoBruto"].append(textoCodigo.text.rstrip().lstrip())
                    dicCodigoPython["codigoEnunciado"].append(textoCodigo.text.rstrip().lstrip())
            dicCodigoPython["codigoBruto"]="\n\n".join(dicCodigoPython["codigoBruto"])
            dicCodigoPython["codigoEnunciado"]="\n\n".join(dicCodigoPython["codigoEnunciado"])
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
                codigoPyConEntrada=acceso.make_tempPython2(dicCodigoPython["codigoBruto"], funcionTracer, testEstandar, funcionEntrada)
                dicCodigoPython["codigo"].append(codigoPyConEntrada)
            #dicCodigoPython["codigoBruto"]=codigoPython.text.rstrip().lstrip()
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
    definicion={} #Para el tipo pregunta definicion
    definicion["termino"]=[]
    definicion["codigo"]=[]
    caracterEspaciador="@" #por cada caracter espaciador en el contenido, lo reemplazara por 4 espacios  
    link=[]
    enunciado="" #Para el tipo pregunta enunciadoIncompleto
    shuffleanswers=""
    penalty=""
    answernumbering=""
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
        try:
            shuffleanswers=int(subRaiz.attrib['shuffleanswers'])
            if shuffleanswers==1:
                shuffleanswers=str(shuffleanswers)
            elif shuffleanswers==0:
                shuffleanswers=str(shuffleanswers)
            else:
                shuffleanswers="1"
        except:
            shuffleanswers="1"
        try:
            penalty=float(subRaiz.attrib['penalty'])
            if penalty>puntaje:
                penalty=puntaje
            penalty=str(penalty)
        except:
            penalty="0"
        try:
            answernumbering=str(subRaiz.attrib['answernumbering'])
            if determinaNumerado(answernumbering)=="N":
                answernumbering="abc"
        except:
            answernumbering="abc"
        try:
            link=str(subRaiz.attrib['link'])
            if ";" in link:
                link=link.split(";")
            elif "," in link:
                link=link.split(",")
            elif "+" in link:
                link=link.split("+")
            elif "-" in link:
                link=link.split("-")
            else:
                if link in [None,""]:
                    link=[]
                else:
                    pass
        except:
            link=[]
    if tipo=='definicion':      
        try:
            caracterEspaciador=str(subRaiz.attrib['caracterEspaciador'])
        except:
            caracterEspaciador="@"
        for subRaiz in raizXmlEntrada.iterfind('termino'):
            for trozoEnunciado in subRaiz.iter():
                if trozoEnunciado.tag=="text":
                    definicion["termino"].append(trozoEnunciado.text.rstrip().lstrip())
                elif trozoEnunciado.tag=="codigo":
                    definicion["codigo"].append(trozoEnunciado.text.rstrip().lstrip())
        definicion["termino"]=" ".join(definicion["termino"])
        definicion["codigo"]="\n\n".join(definicion["codigo"])
    elif tipo=='pythonCompara':
        listaCodigosPorEntrada, comentarios=analizadorComparacion(raizXmlEntrada)
        return xmlEntrada.xmlEntrada(nombreArchivo,tipo,puntaje,conjuntoAlternativas,cantidadAlternativas,shuffleanswers,penalty,answernumbering,link,codigos=listaCodigosPorEntrada,comentarios=comentarios,idOrigenEntrada=idOrigenEntrada)

    elif tipo=='pythonIterativo' or tipo=='pythonIterativoInvertido':
        listaCodigosPython=analizadorIteracion(raizXmlEntrada)
        return xmlEntrada.xmlEntrada(nombreArchivo,tipo,puntaje,conjuntoAlternativas,cantidadAlternativas,shuffleanswers,penalty,answernumbering,link,codigos=listaCodigosPython,idOrigenEntrada=idOrigenEntrada)

    elif tipo=='pythonTraza':
        listaCodigosPython=analizadorTraza(raizXmlEntrada)
        return xmlEntrada.xmlEntrada(nombreArchivo,tipo,puntaje,conjuntoAlternativas,cantidadAlternativas,shuffleanswers,penalty,answernumbering,link,codigos=listaCodigosPython,idOrigenEntrada=idOrigenEntrada)

    elif tipo=='enunciadoIncompleto':
        respuestas={}
        distractores={}
        idOrden={}
        #spacer="-"
        contadorPosOrden=0
        contadorIDprovisorio=0
        presenciaBlank=False
        enunciadoIncompleto=[]
        idActual=""
        banderaPrimeraGlosa=True
        caracterSeparador="-" #es aquel que separa las alternativas
        caracterResaltador="" #es aquel que rodea las alternativas
        largoBlank=15
        ##Obtencion de parametros propios de modulo enunciadoIncompleto
        try:
            caracterResaltador=str(subRaiz.attrib['caracterResaltador'])
        except:
            caracterResaltador=""
        try:
            caracterSeparador=str(subRaiz.attrib['caracterSeparador'])
        except:
            caracterSeparador="-"
        try:
            caracterEspaciador=str(subRaiz.attrib['caracterEspaciador'])
        except:
            caracterEspaciador="@"
        try:
            largoBlank=int((subRaiz.attrib['largoBlank']))
        except:
            largoBlank=15
        ############################################################
        for subRaiz in raizXmlEntrada.iterfind('enunciado'):
            for parteEnunciado in subRaiz:
                if parteEnunciado.tag=='glosa':
                    if banderaPrimeraGlosa==True:
                        enunciadoIncompleto.append(parteEnunciado.text.rstrip().lstrip())
                        banderaPrimeraGlosa=False
                    else:
                        enunciadoIncompleto.append(parteEnunciado.text)
                if parteEnunciado.tag=='blank':
                    #####
                    try:
                        if parteEnunciado.attrib["id"] in respuestas.keys():
                            print "Error X: El documento '"+nombreArchivo+"' presenta una seccion blank con una ID duplicada"
                            exit()  
                        else:
                            idActual=parteEnunciado.attrib["id"]
                            idOrden[contadorIDprovisorio]=idActual
                            contadorIDprovisorio+=1
                            respuestas[idActual]=[]
                    except:
                            print "Error X: El documento '"+nombreArchivo+"' presenta una seccion blank sin ID"
                            exit()
                        ####
                    for textoBlank in parteEnunciado.iterfind('text'):
                        #largoBlank=len(textoBlank.text.rstrip().lstrip())
                        respuestas[idActual].append({"glosa":textoBlank.text.rstrip().lstrip(),"tipo":"solucion"})
                        presenciaBlank=True
                        #if largoBlank>largoCadenaBlank:
                        #    largoCadenaBlank=largoBlank
                    if presenciaBlank==False:
                        print "Error 3: El documento '"+nombreArchivo+"' no presenta terminos en el tag 'blank' que representan las alternativas solucion del item"
                        exit()
                    enunciadoIncompleto.append('_'*largoBlank)
                    presenciaBlank=False         
        enunciado=' '.join(enunciadoIncompleto)
        enunciado=enunciado.replace(caracterEspaciador,"&emsp;"*4)
        for opcion in raizXmlEntrada.iterfind('opciones'):
            
            for alternativa in opcion.iterfind('alternativa'):
                try:
                    if not alternativa.attrib['id'] in respuestas.keys():
                        print "Error X: El documento '"+nombreArchivo+"' presenta un distractor con una ID no coincidente con las secciones blank y se ha omitido"
                        continue
                    else:
                        idActual=alternativa.attrib['id']
                        distractores[idActual]=[]
                except:
                        print "Error X: El documento '"+nombreArchivo+"' presenta una seccion alternativa sin ID"
                        exit()
                glosaYComentario={}
                for glosa in alternativa.iterfind('glosa'):
                    comentarioMerged=""
                    glosaYComentario["glosa"]=glosa.text.rstrip().lstrip()
                    try:
                        glosaYComentario["id"]=glosa.attrib["id"]
                    except:
                        print "Precaucion X: una glosa de  '"+nombreArchivo+"' no tiene id y se ha omitido"
                        continue
                    glosaYComentario["tipo"]='distractor'
                    for comentario in glosa.iterfind('comentario'):
                        comentarioMerged+=comentario.text.rstrip().lstrip()+' '
                    glosaYComentario["comentario"]=comentarioMerged
                    distractores[idActual].append(copy.copy(glosaYComentario))
        conjuntoAlternativas={}
        #respuestas["id"]=lista de glosas sinonimas
        #distractores["id"]=lista de diccionarios tipo{"glosa":string,"comentario":string}
        conjuntoAlternativas["respuestas"]=respuestas
        conjuntoAlternativas["distractores"]=distractores
        #tabla hash que indica el orden de aparicion de los blank sin importar la id
        conjuntoAlternativas["idOrden"]=idOrden
        return xmlEntrada.xmlEntrada(nombreArchivo,tipo,puntaje,conjuntoAlternativas,cantidadAlternativas,shuffleanswers,penalty,answernumbering,link,enunciado=enunciado, idOrigenEntrada=idOrigenEntrada, caracterResaltador=caracterResaltador, caracterSeparador=caracterSeparador)
        #alternativaSolucion=list()
        #alternativaSolucion.append(alternativa.alternativa(hashlib.sha256('solucion').hexdigest(),'solucion',str(puntaje),'-'.join(respuestas),comentario='Alternativa Correcta',numeracion=1))
        #conjuntoAlternativas[alternativaSolucion[0].llave]=alternativaSolucion
    elif tipo=='definicionPareada':
        #Valores por default
        composicionDistractores="1+2"
        criterioOrdenDistractores="None"
        ordenTerminos="None"
        parcialScore="N"
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
                if bool(str(subRaiz.attrib['parcialScore']).rstrip())==True:
                    parcialScore=strToSN(subRaiz.attrib['parcialScore'])
                    #print parcialScore
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
                contAltSinonima=0
                for par in glosa.iter('par'):
                    contAltSinonima=contAltSinonima+1
                    pozoPares.append(ALT.alternativa(glosa.attrib['id']+str(contAltSinonima),'solucion',str(puntaje),par.text.rstrip()))
                contAltSinonima=0
                for inpar in glosa.iter('inpar'):
                    textoComentario=[]
                    contAltSinonima=contAltSinonima+1
                    for comentario in inpar.iter('comentario'):
                        textoComentario.append(comentario.text.rstrip())
                    #textoComentario=textoComentario.lstrip()
                    #agrego solo si existe el inpar
                    if bool(inpar.text.rstrip())==True:
                        pozoImpares.append(ALT.alternativa(glosa.attrib['id']+str(contAltSinonima),'distractor','0',inpar.text.rstrip(),comentario=" ".join(textoComentario)))
                conjuntoTerminosPareados[definicion.rstrip()]=pozoPares
                #No es necesario agregar una llave si no tiene impares
                if len(pozoImpares)>0:
                    conjuntoTerminosImpares[definicion.rstrip()]=pozoImpares
            conjuntoAlternativas['terminos']=conjuntoTerminosPareados
            conjuntoAlternativas['distractores']=conjuntoTerminosImpares
        #Se puede retornar antes el de definicion pareada, pues no presenta seccion opciones, sino una seccion completa de definiciones con sus pares e impares
        #Ademas este tipo de pregunta tiene mas atributos
        return xmlEntrada.xmlEntrada(nombreArchivo,tipo,puntaje,conjuntoAlternativas,cantidadAlternativas,shuffleanswers,penalty,answernumbering,link,enunciado=enunciado,composicionDistractores=composicionDistractores,criterioOrdenDistractores=criterioOrdenDistractores,ordenTerminos=ordenTerminos,cantidadCombinacionesDefiniciones=cantidadCombinacionesDefiniciones, idOrigenEntrada=idOrigenEntrada,parcialScore=parcialScore)
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
                if idAlternativa in conjuntoAlternativas.keys():
                    largoLista=len(conjuntoAlternativas[opcion.attrib['id']])
                    if tipoOpcion=="solucion":
                        conjuntoAlternativas[opcion.attrib['id']].append(ALT.alternativa(opcion.attrib['id'],opcion.attrib['tipo'],str(puntaje),glosaOpcion.text.rstrip(),comentario=comentarioAlternativa,numeracion=largoLista+1))
                    else:
                        conjuntoAlternativas[opcion.attrib['id']].append(ALT.alternativa(opcion.attrib['id'],opcion.attrib['tipo'],str(0),glosaOpcion.text.rstrip(),comentario=comentarioAlternativa,numeracion=largoLista+1))
                else:
                    conjuntoAlternativas[opcion.attrib['id']]=list()
                    try:
                        if opcion.attrib['tipo']=="solucion":
                            conjuntoAlternativas[opcion.attrib['id']].append(ALT.alternativa(opcion.attrib['id'],opcion.attrib['tipo'],str(puntaje),glosaOpcion.text.rstrip(),comentario=comentarioAlternativa,numeracion=1))
                        else:
                            conjuntoAlternativas[opcion.attrib['id']].append(ALT.alternativa(opcion.attrib['id'],opcion.attrib['tipo'],str(0),glosaOpcion.text.rstrip(),comentario=comentarioAlternativa,numeracion=1)) 
                    except:
                        print "Error1: El atributo tipo contiene un nombre distinto de 'solucion' o 'distractor'"
                        exit()                    
    return xmlEntrada.xmlEntrada(nombreArchivo,tipo,puntaje,conjuntoAlternativas,cantidadAlternativas,shuffleanswers,penalty,answernumbering,link,termino=definicion["termino"],codigo=definicion["codigo"],enunciado=enunciado, idOrigenEntrada=idOrigenEntrada, caracterEspaciador=caracterEspaciador )

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
        if elem.tag=='answer':
            subRaizOpciones.remove(elem)
    for alternativa in listaAlternativas:
        identificadorPregunta+=alternativa.identificador()
        opcion = ET.SubElement(subRaizOpciones, 'answer')
        opcionText=ET.SubElement(opcion, 'text')
        opcionText.text=alternativa.glosa
        glosasAlternativas+=alternativa.glosa
        opcion.set('puntaje',alternativa.puntaje)
        opcion.set('id',alternativa.llave)
        opcion.set('tipo',alternativa.tipo)
        if (alternativa.tipo=="solucion"):
            opcion.set('fraction',"100")
        else:
            opcion.set('fraction',"0")
        feedBack=ET.SubElement(opcion, 'feedback')
        feedbackText=ET.SubElement(feedBack, 'text')
        feedbackText.text=alternativa.comentario
    #A partir del texto concatenado, se crea una unica ID que representa las alternativas
    #Esta ID se asigna a un nuevo atributo a la subRaiz 'opciones'
    idItem=hashlib.sha256(glosasAlternativas).hexdigest()
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
            yield '>'# + '\n'
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

def escribePlantilla2(directorioSalida,tipoPregunta,nombreArchivo,raizXML,formato,informacionXML,estilo,**kwargs):
    banderaMerge=False
    DECLARATION=""
    archivoSalida=""
    if 'merge' in kwargs.keys():
        if kwargs['merge']=='merge':
            modoEscritura='a'
            banderaMerge=True
            acceso.CrearDirectorio(directorioSalida+'/'+tipoPregunta)
            archivoSalida=open(directorioSalida+'/'+tipoPregunta+'-'+'Output'+'.'+formato,'a')
        else:
            archivoSalida=open(directorioSalida+'/'+nombreArchivo+'.'+formato, 'w')
    else:
        archivoSalida=open(directorioSalida+'/'+nombreArchivo+'.'+formato, 'w')
    #acceso.CrearDirectorio(directorioSalida+'/'+tipoPregunta)
    tree = ET.ElementTree(raizXML)
    if banderaMerge==False:
        DECLARATION = """<?xml version="1.0" encoding="utf-8"?>\n"""
        #nombreArchivoSalida=directorioSalida+'/'+nombreArchivo+'.'+formato
    ESTILO=""
    if estilo=='no':
        pass
    else:
        if banderaMerge==False:
            ESTILO = '<?xml-stylesheet href="../../css/'+estilo+'.css" title="Estilo Estandar"?>\n'
    #tree = ET.parse(filename)
    # do some work on tree
    with archivoSalida as output: # would be better to write to temp file and rename
        if informacionXML=='si':
            output.write(DECLARATION)
        if estilo!='no':
            output.write(ESTILO)
       # output.write(xmlprettyprint(raizXML))
        output.write(ET.tostring(raizXML, 'utf-8', method="xml"))
        #tree.write(output, xml_declaration=False, encoding='utf-8')
    archivoSalida.close()
    pass

def mergeOperation(directorioSalida,tipoPregunta,formato,modo,formatoXML,estilo):
    DECLARATION = """<?xml version="1.0" encoding="utf-8"?>\n"""
    ESTILO = '<?xml-stylesheet href="../../css/'+estilo+'.css" title="Estilo Estandar"?>\n'
    if modo=='open':
        #Se borra el archivo
        acceso.CrearDirectorio(directorioSalida+'/'+tipoPregunta)
        archivoSalida=open(directorioSalida+'/'+tipoPregunta+'-'+'Output'+'.'+formato,'w')
        archivoSalida.write('')
        archivoSalida.close()
        archivoSalida=open(directorioSalida+'/'+tipoPregunta+'-'+'Output'+'.'+formato,'a')
        if formatoXML=='si':
            archivoSalida.write(DECLARATION)
        if estilo!='no':
            archivoSalida.write(ESTILO)
        archivoSalida.write('<quiz>\n')
        archivoSalida.close()
    else:
        archivoSalida=open(directorioSalida+'/'+tipoPregunta+'-'+'Output'+'.'+formato,'a')
        archivoSalida.write('</quiz>')
        archivoSalida.close()