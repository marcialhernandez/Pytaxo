#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import sys
import itertools, hashlib, threading, copy, logging
from archivos import nombres, xmlSalida
from clases import plantilla, alternativa


try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    
logging.basicConfig( level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

class Total(object):
    
    def __init__(self, valorInicial=0):
        self.lock = threading.Lock()
        self.valor = valorInicial
        
    def incrementar(self,incremento):
        logging.debug('Waiting for lock')
        self.lock.acquire()
        try:
            logging.debug('Acquired lock')
            self.valor = self.valor + incremento
        finally:
            self.lock.release()

#Convierte una lista de lista de alternativas en una lista de alternativas
def comprimeAlternativas(MatrizAlternativas):
    listaAlternativasComprimidas=list()
    for cadaListaAlternativas in MatrizAlternativas:
        listaAlternativasComprimidas.append(comprimeAlternativasSingle(cadaListaAlternativas))
    return listaAlternativasComprimidas

#Convierte lista de alternativas en una alternativa
##(Debido a que cada alternativa es realidad un grupo de terminos que tambien son alternativas)
def comprimeAlternativasSingle(listaAlternativas):
    llave=''
    tipo=''
    puntaje=0
    glosa=''
    comentarios=''
    for cadaAlternativa in listaAlternativas:
        llave+=cadaAlternativa.llave
        if cadaAlternativa.tipo not in tipo:
            tipo+=cadaAlternativa.tipo+' '
        puntaje+=int(cadaAlternativa.puntaje)
        glosa+='"'+cadaAlternativa.glosa+'" ' #se debe agregar con rstrip()
        if hasattr(cadaAlternativa,'comentario')==True:
            comentarios+='"'+cadaAlternativa.comentario+'" '
        else:
            if cadaAlternativa.tipo=='solucion':
                comentarios+='"Termino correcto"'+' '
            else:
                comentarios+='"Sin comentario"'+' '
    if 'solucion' in tipo and 'distractor' in tipo:
        tipo='distractor'
    #puntaje=float(puntaje)/cantidadAlternativas
    #print puntaje
    return alternativa.alternativa(llave,tipo.rstrip(),float(puntaje)/len(listaAlternativas),glosa.rstrip(),comentario=comentarios.rstrip())
        
#No preserva el orden y no admite datos tipo list() como por ejemplo matrices  
def quitaDuplicados(seq):
    return {}.fromkeys(seq).keys()
    
def retornaSignificadoCadena(cadenaSimbolos,xmlEntradaObject,distractores,solucion,cantidadAlternativas,**kwuargs):
    listaCombinatoria=list()
    listaConjuntoAlternativas=list()
    listaConjuntoDistractores=None
    #Caso en que tenga varios comandos
    if '+' in cadenaSimbolos:
        for simbolos in quitaDuplicados(cadenaSimbolos.split('+')):
            for conjunto in retornaSignificadoSimbolo(simbolos, xmlEntradaObject, distractores, solucion):
                if conjunto not in listaCombinatoria:
                    listaCombinatoria.append(conjunto)
        listaConjuntoDistractores=list(itertools.combinations(listaCombinatoria, cantidadAlternativas))
    else:
        listaConjuntoDistractores=list(itertools.combinations(retornaSignificadoSimbolo(cadenaSimbolos, xmlEntradaObject, distractores, solucion), cantidadAlternativas))
    if len(listaConjuntoDistractores)>0:
        for conjunto in listaConjuntoDistractores:
            conjunto=list(conjunto)
            conjunto.append(comprimeAlternativasSingle(solucion))
            if 'orderBy' in kwuargs.keys():
                if kwuargs['orderBy'].lower()=='largocreciente':
                    conjunto.sort(key=lambda x:len(x.glosa))
                elif kwuargs['orderBy'].lower()=='largodecreciente':
                    conjunto.sort(key=lambda x:len(x.glosa),reverse=True)
                elif kwuargs['orderBy'].lower()=='alfabeticocreciente':
                    conjunto.sort(key=lambda x:x.glosa.lower)
                elif kwuargs['orderBy'].lower()=='alfabeticodecreciente':
                    conjunto.sort(key=lambda x:x.glosa.lower,reverse=True)
                else:
                    #No se ordena quedando la alternativa solucion siempre al final
                    pass
                #Luego se agrega el conjunto al conjunto de alternativas Validas
                listaConjuntoAlternativas.append(conjunto)
            #Si no se presenta el comando, no se ordena quedando la alternativa solucion siempre al final
            else:
                listaConjuntoAlternativas.append(conjunto)
    return listaConjuntoAlternativas

def retornaSignificadoSimbolo(simbolo,xmlEntradaObject,distractores,solucion):
    simbolo=simbolo.lstrip().rstrip().lower()
    if simbolo.isdigit()==True:
        if int(simbolo)<=0:
            return list()
        else:
            return pozoDistractoresNesimo(xmlEntradaObject,distractores,int(simbolo),solucion=solucion)
    else:
        return list()

def posiblesSolucionesYDistractoresConjunto(xmlEntradaObject,conjuntoTerminos):
    salida=dict()
    listaDeListaDeOpciones=list()
    distractores=list()        
    for cadaDefinicion in conjuntoTerminos:
        posiblesTerminos=list()
        for cadaTermino in xmlEntradaObject.alternativas['terminos'][cadaDefinicion]:
            posiblesTerminos.append(cadaTermino)
        listaDeListaDeOpciones.append(posiblesTerminos)
        if cadaDefinicion in xmlEntradaObject.alternativas['distractores'].keys():
            #Con esto se evita errores de intentar acceder a una llave que no existe
            for cadaDistractor in xmlEntradaObject.alternativas['distractores'][cadaDefinicion]:
                distractores.append(cadaDistractor)
    #Se obtiene una lista de posibles soluciones de la variante actual
    salida['soluciones']=list(itertools.product(*listaDeListaDeOpciones))
    salida['distractores']=distractores
    return salida

#def pozoDistractoresNesimo(xmlEntradaObject,solucion,distractores,cantidadDistractores,**kwargs):#cantidadDistractores,pozoNesimo)
def pozoDistractoresNesimo(xmlEntradaObject,distractores,cantidadReemplazoDistractores,**kwargs):#cantidadDistractores,pozoNesimo)
    #Implica que es el primer ciclo
    if 'solucion' in kwargs.keys():
        pozoDistractoresN=list()
        #Si quiere 0 reemplazos por los distractores, , es la solucion misma
        if cantidadReemplazoDistractores<=0 or len(distractores)==0:
            pozoDistractoresN.append(kwargs['solucion'])
            return pozoDistractoresN
        #Se valida que la cantidad de distractores pedidos puedan ser soportados por los distractores que se piden
        #En caso que no hayan distractores, no se realizara este proceso
        if len(xmlEntradaObject.alternativas['distractores'].keys())<=cantidadReemplazoDistractores:
            cantidadReemplazoDistractores=len(xmlEntradaObject.alternativas['distractores'].keys())
        for cadaDistractor in distractores:
            contador=0
            for cadaTermino in kwargs['solucion']:
                if cadaTermino.llave==cadaDistractor.llave:
                    conjuntoDistractor=list(kwargs['solucion'])
                    conjuntoDistractor[contador]=cadaDistractor
                    if conjuntoDistractor not in pozoDistractoresN:
                        pozoDistractoresN.append(conjuntoDistractor)
                    break
                contador+=1
        cantidadReemplazoDistractores=cantidadReemplazoDistractores-1
        #Se termina recursion 
        if cantidadReemplazoDistractores==0:
            return comprimeAlternativas(pozoDistractoresN)
                
        else:
            return pozoDistractoresNesimo(xmlEntradaObject,distractores,cantidadReemplazoDistractores,nuevoPozo=pozoDistractoresN)
    #Implica que es el nesimo ciclo
    if 'nuevoPozo' in kwargs.keys():
        pozoDistractoresD=list()
        for cadaConjunto in kwargs['nuevoPozo']:
            for cadaDistractor in distractores:
                contador=0
                for cadaTermino in cadaConjunto:
                    if cadaTermino.llave==cadaDistractor.llave and cadaTermino.tipo=='solucion':
                        conjuntoDistractor=cadaConjunto[:]
                        conjuntoDistractor[contador]=cadaDistractor
                        if conjuntoDistractor not in pozoDistractoresD:
                            pozoDistractoresD.append(conjuntoDistractor)
                        break
                    contador+=1
        cantidadReemplazoDistractores=cantidadReemplazoDistractores-1
        if cantidadReemplazoDistractores==0:
            return comprimeAlternativas(pozoDistractoresD)
        else:
            return pozoDistractoresNesimo(xmlEntradaObject,distractores,cantidadReemplazoDistractores,nuevoPozo=pozoDistractoresD)

#No es solucion pues uno de sus terminos es en realidad un distractor
#reemplazar 1 elemento
#de la solucion por 1 de la lista de distractores
#el reemplazo tiene que se por ID, significa que se reemplaza
#un termino por su propio distractor
def pozoDistractoresSingle(xmlEntradaObject,solucion,distractores):
    pozoDistractoresS=list()
    if len(distractores)>=1:
        #En caso que no hayan distractores, no se realizara este proceso
        for cadaDistractor in distractores:
            contador=0
            for cadaTermino in solucion:
                if cadaTermino.llave==cadaDistractor.llave:
                    conjuntoDistractor=list(solucion)
                    conjuntoDistractor[contador]=cadaDistractor
                    if conjuntoDistractor not in pozoDistractoresS:
                        pozoDistractoresS.append(conjuntoDistractor)
                    break
                contador+=1
    return pozoDistractoresS

def pozoDistractoresDouble(xmlEntradaObject,solucion,distractores):
    pozoDistractoresD=list()
    #En caso que no hayan mas de un tipo de distractor, no se realizara este proceso
    if len(xmlEntradaObject.alternativas['distractores'].keys())>1:
        pozoDistractoresS=pozoDistractoresSingle(xmlEntradaObject, solucion, distractores)
        for cadaConjunto in pozoDistractoresS:
            for cadaDistractor in distractores:
                contador=0
                for cadaTermino in cadaConjunto:
                    if cadaTermino.llave==cadaDistractor.llave and cadaTermino.tipo=='solucion':
                        conjuntoDistractor=cadaConjunto[:]
                        conjuntoDistractor[contador]=cadaDistractor
                        if conjuntoDistractor not in pozoDistractoresD:
                            pozoDistractoresD.append(conjuntoDistractor)
                        break
                    contador+=1
    return pozoDistractoresD

#Admite entrada kwuargs[] 'especificacion' de la forma
#2+1 ->alternativas derivadas de distractores con 1 y 2 reemplazos
#1+1 ->alternativas derivadas de distractores con 1 reemplazo (se eliminan repetidos)
#2 ->alternativas derivadas de distractores que tienen si o si 2 reemplazos
#admite n sumas, pero entre más tenga, más recursos utiliza
#ejemplo -> 1+2+3
#0 ->retorna una lista vacia
#0+1 -> genera alternativas derivadas de distractores que tienen si o si 1 reemplazo  
#En caso que no se especifique, genera alternativas correspondientes a la entrada 1+2
#Admite entrada kwuargs[] 'orderBy' para ordenar los conjuntos por medio de un criterio
#Admite entrada kwuargs[] 'creciente', si es True los ordena de menor a mayor, False de menor a mayor
#Los criterios disponibles son largo y alfabetico, por default sin orden y la solucion sera la ultima alternativa

def agrupamientoPareado(xmlEntradaObject,solucion,distractores,cantidadAlternativas,**kwuargs):
    if 'especificacion' in kwuargs.keys():
        if 'orderBy' in kwuargs.keys():
            return retornaSignificadoCadena(kwuargs['especificacion'],xmlEntradaObject,distractores,solucion,cantidadAlternativas-1,orderBy=kwuargs['orderBy'])
        else:
            return retornaSignificadoCadena(kwuargs['especificacion'],xmlEntradaObject,distractores,solucion,cantidadAlternativas-1)    
    #default ->1+2
    else:
        if 'orderBy' in kwuargs.keys():
            return retornaSignificadoCadena('1+2',xmlEntradaObject,distractores,solucion,cantidadAlternativas-1,orderBy=kwuargs['orderBy'])
        else:
            return retornaSignificadoCadena('1+2',xmlEntradaObject,distractores,solucion,cantidadAlternativas-1)
        
    #Valida el correcto funcionamiento, reemplazando el return por listaAlternativas
#     print type(listaAlternativas)
#     print len(listaAlternativas)
#     for conjunto in listaAlternativas:
#         print 'conjunto'
#         for elem in conjunto:
#             print elem.tipo           

def procesoPareador(conjuntoDefiniciones,plantillaSalida,xmlEntradaObject,cantidadAlternativas,banderaEstado,directorioSalida, total): #Se tiene que pasar una copia de subraizSalida si se quiere utilizar con hebras
    #falta revisar como hacer que todas las hebras puedan incrementar el total, para luego imprimirlo
    #de momento cada una lo incrementa, pero este efecto no se ve reflejado en la variable global
    subRaizSalida=None
    for elem in plantillaSalida.iter('opciones'):
        subRaizSalida=elem
#     Proceso necesario cuando era monohebra
#     for elem in subRaizSalida.getchildren():
#         subRaizSalida.remove(elem)
    contador=0
#     for elem in subRaizSalida.getchildren():
#         subRaizSalida.remove(elem)
    seccionDefiniciones=ET.SubElement(subRaizSalida,'definiciones')
    idPreguntaGenerada=""
    for definicion in conjuntoDefiniciones:
        subRaizDefinicion=ET.SubElement(seccionDefiniciones,'definicion')
        subRaizDefinicion.text=definicion
        idPreguntaGenerada+=definicion+' '
    idPreguntaGenerada=hashlib.sha256(idPreguntaGenerada.rstrip()).hexdigest()
    for x in plantillaSalida.iter('plantilla'): x.set('id', idPreguntaGenerada)               
    #Seccion donde estaran los terminos
    seccionTerminos=ET.SubElement(subRaizSalida,'terminos')
    #Seccion donde estaran las alternativas
    seccionAlternativas=ET.SubElement(subRaizSalida,'conjuntoAlternativas')
    #Aqui se presenta cada posible pregunta
    solucionesYDistractores=posiblesSolucionesYDistractoresConjunto(xmlEntradaObject,conjuntoDefiniciones)
    #Para cada solucion de la variante actual 
    for solucion in solucionesYDistractores['soluciones']:
        listaTerminos=list(solucion)+solucionesYDistractores['distractores']
        #Aqui se presenta el ordenamiento en que aparecen los terminos en el enunciado
        #Por default sera alfabetico creciente
        if xmlEntradaObject.ordenTerminos.lower()=='alfabeticocreciente':
            listaTerminos.sort(key=lambda x:x.glosa.lower())
        elif xmlEntradaObject.ordenTerminos.lower()=='alfabeticodecreciente':
            listaTerminos.sort(key=lambda x:x.glosa.lower, reverse=True)
        elif xmlEntradaObject.ordenTerminos.lower()=='largocreciente':
            listaTerminos.sort(key=lambda x:len(x.glosa))
        elif xmlEntradaObject.ordenTerminos.lower()=='largodecreciente':
            listaTerminos.sort(key=lambda x:len(x.glosa), reverse=True)
        else:
            #No se ordena
            pass 
        #Por cada ciclo debo eliminar los hijos de la seccion terminos y poner los nuevos
        for elem in seccionTerminos.getchildren():
            seccionTerminos.remove(elem)
        #Agrego los posibles terminos
        for cadaTermino in listaTerminos:
            subRaizTermino=ET.SubElement(seccionTerminos,'posiblePar')
            subRaizTermino.text=cadaTermino.glosa
            subRaizTermino.set('id',cadaTermino.llave)
        #solucion provisional
        ordenamientoDiferente=0 #indica que es el mismo grupo de alternativas pero estan ordenados de forma diferente
        for cadaConjunto in agrupamientoPareado(xmlEntradaObject,solucion,solucionesYDistractores['distractores'],cantidadAlternativas,especificacion=xmlEntradaObject.composicionDistractores, orderBy=xmlEntradaObject.criterioOrdenDistractores):
            for elem in seccionAlternativas.getchildren():
                seccionAlternativas.remove(elem)
            glosasAlternativas=""
            idAlternativas=""
            for cadaTermino in cadaConjunto:
                subRaizAlternativa=ET.SubElement(seccionAlternativas,'alternativa')
                subRaizAlternativa.text=cadaTermino.glosa
                glosasAlternativas+=cadaTermino.glosa
                subRaizAlternativa.set('puntaje',str(cadaTermino.puntaje))
                subRaizAlternativa.set('id',cadaTermino.llave)
                subRaizAlternativa.set('tipo',cadaTermino.tipo)
                subRaizComentario=ET.SubElement(subRaizAlternativa,'comentario')
                subRaizComentario.text=cadaTermino.comentario
                idAlternativas+=cadaTermino.identificador()
                subRaizSalida.set('idAlternativasGenerada',idAlternativas.rstrip())
            ordenamientoDiferente+=1
#                                 if contador==4:
#                                     print str(contador)+' Creados'  
#                                     return 0      
            if banderaEstado==True:
                #Se instancia la plantilla como un elemento de element tree
                xmlSalida.escribePlantilla(directorioSalida,xmlEntradaObject.tipo,threading.currentThread().getName()+ idPreguntaGenerada+' '+idAlternativas.rstrip()+' '+str(ordenamientoDiferente) +' '+str(contador), plantillaSalida,'xml')
                
            else:
                print ET.tostring(plantillaSalida, 'utf-8', method="xml")
            contador+=1
    #Condicion de carrera
    total.incrementar(contador)
    #Descomentar para validar funcionamiento
    #print threading.currentThread().getName()+' '+str(total.valor)
    return 0
    #print contador
    #pass

#Funcion que analiza la plantilla que corresponde a este tipo de pregunta
#A esa plantilla se le añaden los datos obtenidos desde la entrada de
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
            validaPlantilla=False
    return plantillasValidas

def retornaPlantilla(nombreDirectorioPlantillas,xmlEntradaObject,cantidadAlternativas, tipoPregunta, **kwuargs): #,xmlEntradaObject):
    #Esto era requerido cuando se tomaba como tipo el nombre de la plantilla, y no un atributo incrustado en el xml
    #tipoPregunta=nombres.nombreScript(__file__)
    #Variable compartida, pues cada hebra aumenta el total de archivos creados
    total=Total()
    hilos=[]
    listaDeConjuntoDefiniciones=list()
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
                    cantidadCombinacionesDefiniciones=0
                    #Si la cantidad de combinaciones de definiciones es 0, no se genera nada
                    if xmlEntradaObject.cantidadCombinacionesDefiniciones==0:
                        pass
                    #Si la cantidad de combinaciones de definiciones es 1, se trabaja con la entrada
                    #tal como se ingreso por el usuario
                    elif xmlEntradaObject.cantidadCombinacionesDefiniciones==1:
                        listaDeConjuntoDefiniciones.append(xmlEntradaObject.alternativas['terminos'].keys())
                    else:
                        listaDeConjuntoDefiniciones=xmlEntradaObject.barajaDefiniciones()    
                    for conjuntoDefiniciones in listaDeConjuntoDefiniciones:
                        if xmlEntradaObject.cantidadCombinacionesDefiniciones==cantidadCombinacionesDefiniciones:
                            break
                        t = threading.Thread(target=procesoPareador, args=(conjuntoDefiniciones,copy.deepcopy(plantillaSalida),xmlEntradaObject, cantidadAlternativas,banderaEstado,kwuargs['directorioSalida'],total) )
                        t.setDaemon(True)
                        hilos.append(t)
                        t.start()
                        t.join()
                        cantidadCombinacionesDefiniciones+=1
    #Se imprime solo si se especifica directorio de salida
    if banderaEstado==True:
        print str(total.valor)+' Creados' 
    return 0                          

# Declaracion de directorio de entradas
nombreDirectorioEntradas="./Entradas/Definiciones"
nombreDirectorioPlantillas="./Plantillas"
nombreDirectorioSalidas="Salidas"
nombreCompilador="python"
tipoPregunta='definicionPareada'
listaXmlEntrada=list()

# Almacenamiento usando el parser para este tipo de pregunta

#Ahora la entrada que indica la cantidad de alternativas viene incrustada como atributo en los respectivos
#XML de entrada
#cantidadAlternativas=xmlSalida.argParse()

if nombres.validaExistenciasSubProceso(nombreDirectorioEntradas)==True:
    listaXmlEntrada=xmlSalida.lecturaXmls(nombreDirectorioEntradas, tipoPregunta)
    
for cadaXmlEntrada in listaXmlEntrada:
    retornaPlantilla(nombreDirectorioPlantillas, cadaXmlEntrada, cadaXmlEntrada.cantidadAlternativas,tipoPregunta, directorioSalida=nombreDirectorioSalidas+'/'+tipoPregunta)