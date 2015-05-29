'''
Created on 16-04-2015

@author: Marcial
'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import sys
import nombres, xmlSalida, acceso, ast,json
import plantilla, alternativa
from matplotlib.cbook import Null
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import subprocess,hashlib, itertools

def borraHijos(ETObject):
    for elem in ETObject.getchildren():
        ETObject.remove(elem)
    pass

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
def incluyeInfo(codigoPython,seccionTrazaSolucion,plantillaSalida,contadorEntradasBruto,enunciado):
    idXmlSalida=""
    idEntradaBruta=str(hashlib.sha256(codigoPython["entradasBruto"][contadorEntradasBruto]).hexdigest())
    seccionTrazaSolucion.set('id', idEntradaBruta)
    seccionTrazaSolucion.set('entradas', codigoPython["entradasBruto"][contadorEntradasBruto])
    for subRaizAux in plantillaSalida.iter():
        if subRaizAux.tag=='plantilla':
            idXmlSalida=codigoPython["id"]+'+'+idEntradaBruta
            subRaizAux.set('id',idXmlSalida)
        if subRaizAux.tag=='enunciado':
            segundaParteEnunciado="Con "
            entradasBrutas=codigoPython["entradasBruto"][contadorEntradasBruto].split(';');
            if len(entradasBrutas)==1:
                glosaEnunciado=" como entrada."
            else:
                glosaEnunciado=" como entradas."    
            for entradaBruta in entradasBrutas:
                segundaParteEnunciado=segundaParteEnunciado+entradaBruta+"; "
            segundaParteEnunciado=segundaParteEnunciado.strip('; ')
            segundaParteEnunciado=segundaParteEnunciado+glosaEnunciado 
            subRaizAux.text=enunciado.replace("@nombreFuncion", codigoPython["nombreFuncionPrincipal"])+" "+segundaParteEnunciado
    seccionComentarios=ET.SubElement(seccionTrazaSolucion,'comentarios')
    seccionComentarios.text=codigoPython["comentarios"]
    return idXmlSalida

def agregaAlternativaIteracion(ETObject,alternativaObject):
    seccionAlternativa=ET.SubElement(ETObject,'alternativa')
    seccionAlternativa.text=alternativaObject.glosa
    seccionAlternativa.set('id', alternativaObject.llave)
    seccionAlternativa.set('tipo',alternativaObject.tipo)
    seccionAlternativa.set('puntaje',str(alternativaObject.puntaje))
    seccionAlternativaComentario=ET.SubElement(seccionAlternativa,'comentario')
    if hasattr(alternativaObject, 'comentario'):
        seccionAlternativaComentario.text=alternativaObject.comentario
    return alternativaObject.llave

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
    #Cuenta la cantidad de items generados
    contador=0
    banderaEstado=False
    enunciado=""
    if 'directorioSalida' in kwuargs.keys():
        banderaEstado=True #Indica si se debe imprimir o no el estado de la cantidad de salidas
    for plantilla in recogePlantillas(nombreDirectorioPlantillas,tipoPregunta):
        plantillaSalida=xmlSalida.plantillaGenericaSalida()
        for subRaizSalida in plantillaSalida.iter():
                enunciado=plantilla.enunciado[:]
                if subRaizSalida.tag=='plantilla':
                    subRaizSalida.set('tipo',xmlEntradaObject.tipo)
                    #subRaizSalida.set('id',xmlEntradaObject.id)
                    subRaizSalida.set('idOrigenEntrada',xmlEntradaObject.idOrigenEntrada)
                #if subRaizSalida.tag=='enunciado':
                #    enunciado=plantilla.enunciado[:]
                    #subRaizSalida.text=plantilla.enunciado
                if subRaizSalida.tag=='opciones':
                    pass
                #Para cada entrada
                    for entrada in xmlEntradaObject.codigos:
                        #Se evalua cada codigo con la entrada actual
                        for codigoAsociado in entrada["codigos"]:
                            streamTraza=obtieneTraza(ejecutaPyTemporal(codigoAsociado["codigo"]))
                            if len(streamTraza)>0:
                                codigoAsociado["retorno"]=streamTraza[-1]['retorno']
                            else:
                                print "El codigo id = "+codigoAsociado["id"]+" no admite la entrada '"+entrada["entrada"]
                                del codigoAsociado
                    
                    cantidadFuncionesAComparar=3 #Siempre son 3, pues si fuesen 2 no se generarian alternativas suficientes
                    for entrada in xmlEntradaObject.codigos:
                        #Aqui es donde se empiezan a crear las formas de los diferentes tipos de preguntas
                        
                         #cantidadFuncionesAComparar debe ser una entrada!!! del xml!!
                        for funcionesComparadas in list(itertools.combinations(entrada["codigos"],cantidadFuncionesAComparar)):
                            #Antes de agregar nueva informacion, se eliminan los hijos
                            borraHijos(subRaizSalida)
                            contadorFunciones=0
                            #Tabla hashNombres creada para asociar cada funcion a un numero
                            hashNombres={}
                            comentarioItem=""
                            #id unico identificador del item, entre los demas items
                            idItem=""
                            seccionesCodigo=[]
                            #Agrego la informacion respecto a las funciones en la glosa del item
                            for funcion in funcionesComparadas:
                                seccionCodigo=ET.SubElement(subRaizSalida,'codigoPython')
                                seccionCodigo.set('id', funcion["id"])
                                seccionCodigo.set('nombreFuncion',funcion["nombreFuncionPrincipal"])
                                seccionesCodigo.append(seccionCodigo)
                                contadorFunciones+=1
                                idItem+=funcion["codigoBruto"]
                                hashNombres[funcion["nombreFuncionPrincipal"]]="I"*contadorFunciones
                                seccionCodigo.text="Funcion "+hashNombres[funcion["nombreFuncionPrincipal"]]+":\n"+funcion["codigoBruto"]
                                comentarioItem+="La funcion "+hashNombres[funcion["nombreFuncionPrincipal"]]+" retorna "+str(funcion["retorno"])+"\n"
                            #falta agregar el valor de las entradas al final de la ID
                            idItem=str(hashlib.sha256(idItem).hexdigest())+"@"+entrada["entradaBruta"]  
                            #Luego se agrega este atributo al tag plantilla, es necesario el for, pues SubRaiz actual es del tag opciones 
                            for subSeccion in plantillaSalida.iter():
                                if subSeccion.tag=='plantilla':
                                    subSeccion.set('id',idItem)
                                #Se aprovecha de agregar el enunciado
                                if subSeccion.tag=='enunciado':
                                    subSeccion.text=enunciado.replace("@entrada",generaGlosaEntradas(entrada["entradaBruta"]))                                   
                            seccionAlternativas=ET.SubElement(subRaizSalida,'alternativas')
                            #Se agrega comentario del item, que menciona el valor de retorno de cada funcion
                            seccionComentario=ET.SubElement(subRaizSalida,'comentario')
                            seccionComentario.text=comentarioItem.rstrip()
                            pozoOpciones=[]
                            #Bandera que indica si todas las funciones comparadas son iguales o no, son iguales si es mayor que 1
                            #Si la banderaTodas es 0, ninguna es igual
                            #Si la banderaTodas es 1, hay por lo menos una igualdad
                            #Si la banderaTodas es 2, todas las funciones son iguales entre si
                            banderaTodas=0 
                            #Tabla hashNombres creada para asociar cada funcion a un numero
                            #hashNombres={}                            
                            for comparaConsulta in list(itertools.combinations(funcionesComparadas,2)):
                                consulta={}
                                consulta["consulta"]=comparaConsulta
                                consulta["glosaAlternativa"]=[] #=comparaConsulta[0]["nombreFuncionPrincipal"]+" y "+comparaConsulta[1]["nombreFuncionPrincipal"]
                                consulta["glosaAlternativa"].append(comparaConsulta[0]["nombreFuncionPrincipal"])
                                consulta["glosaAlternativa"].append(comparaConsulta[1]["nombreFuncionPrincipal"])
                                consulta["idAlternativa"]=[]
                                consulta["idAlternativa"].append(comparaConsulta[0]["id"])
                                consulta["idAlternativa"].append(comparaConsulta[1]["id"])
                                consulta["retorno"]=[]
                                consulta["retorno"].append(comparaConsulta[0]["retorno"])
                                consulta["retorno"].append(comparaConsulta[1]["retorno"])
                                if comparaConsulta[0]["retorno"]==comparaConsulta[1]["retorno"]:
                                    consulta["igualdad"]=True
                                    banderaTodas+=1
                                    
                                else:
                                    consulta["igualdad"]=False
 
                                #print comparaConsulta[0]["nombreFuncionPrincipal"]+"-"+comparaConsulta[1]["nombreFuncionPrincipal"]+"-"+str(consulta["igualdad"])
                                pozoOpciones.append(consulta)
        
                            #reemplazar los nombres de las funciones principales por sus numeros segun la tabla hash
                            for opcion in pozoOpciones:
                                nuevosNombres=[]
                                for nombreFuncion in opcion["glosaAlternativa"]:
                                    nuevosNombres.append(nombreFuncion.replace(nombreFuncion,hashNombres[nombreFuncion]))
                                #Estos son los nombres traducidos segun la tabla hash local creada
                                opcion["glosaAlternativaNumerica"]=nuevosNombres
                                #print " y ".join(opcion["glosaAlternativaNumerica"])
                                #print "+".join(opcion["idAlternativa"])
                            
                            #Aqui es donde se generan las alternativas tipo alternativa
                            #Se generan el pozo de alternativas distractoras y la alternativa solucion
                            listaAlternativasDistractoras=[]
                            alternativaSolucion=""
                            if banderaTodas==0:
                                alternativaSolucion=alternativa("Ninguna", "solucion", xmlEntradaObject.puntaje,"Ninguna")
                                listaAlternativasDistractoras.append(alternativa.alternativa("Todas", "distractor", xmlEntradaObject.puntaje,"I, II y III"))                  
                                for opcion in pozoOpciones:
                                    comentario="La funcion "+opcion["glosaAlternativaNumerica"][0]+ " retorna "+ str(opcion["retorno"][0]) + " y la funcion " +opcion["glosaAlternativaNumerica"][1]+ " retorna "+ str(opcion["retorno"][1])+"."
                                    listaAlternativasDistractoras.append(alternativa.alternativa("+".join(opcion["idAlternativa"]),"distractor",0," y ".join(opcion["glosaAlternativaNumerica"]),comentario=comentario))                  
                                #La alternativa correcta es "ninguna"
                            elif banderaTodas==1:
                                #La alternativa correcta es la consulta contenida en pozoOpciones que tiene el atributo "igualdad"==True
                                listaAlternativasDistractoras.append(alternativa.alternativa("Ninguna", "distractor", xmlEntradaObject.puntaje,"Ninguna"))                  
                                listaAlternativasDistractoras.append(alternativa.alternativa("Todas", "distractor", xmlEntradaObject.puntaje,"I, II y III"))                  
                                for opcion in pozoOpciones:
                                    if opcion["igualdad"]==False:
                                        comentario="La funcion "+opcion["glosaAlternativaNumerica"][0]+ " retorna "+ str(opcion["retorno"][0]) + " y la funcion " +opcion["glosaAlternativaNumerica"][1]+ " retorna "+ str(opcion["retorno"][1])+"."
                                        listaAlternativasDistractoras.append(alternativa.alternativa("+".join(opcion["idAlternativa"]),"distractor",0," y ".join(opcion["glosaAlternativaNumerica"]),comentario=comentario))
                                    else:
                                        alternativaSolucion=alternativa.alternativa("+".join(opcion["idAlternativa"]),"solucion",0," y ".join(opcion["glosaAlternativaNumerica"]))
                            elif banderaTodas==2:
                                #La alternativa correcta es "Todas"
                                alternativaSolucion=alternativa.alternativa("Todas", "solucion", xmlEntradaObject.puntaje,"I, II y III")
                                listaAlternativasDistractoras.append(alternativa.alternativa("Ninguna", "distractor", xmlEntradaObject.puntaje,"Ninguna"))                  
                                for opcion in pozoOpciones:
                                    comentario="La funcion "+opcion["glosaAlternativaNumerica"][0]+ " retorna "+ str(opcion["retorno"][0]) + " y la funcion " +opcion["glosaAlternativaNumerica"][1]+ " retorna "+ str(opcion["retorno"][1])+"."
                                    listaAlternativasDistractoras.append(alternativa.alternativa("+".join(opcion["idAlternativa"]),"distractor",0," y ".join(opcion["glosaAlternativaNumerica"]),comentario=comentario))
                            
                            #Ahora se tiene que hacer la combinatoria del pozo de alternativas distractoras (combinaciones de cantidad de alternativas-1) y a cada una de estas, se le agrega la alternativa correcta al principio
                            #Cada grupo generado es una forma distinta
                            for combinacionAlternativas in list(itertools.combinations(listaAlternativasDistractoras,xmlEntradaObject.cantidadAlternativas-1)):
                                #test=""
                                #Antes de agregar nueva informacion, se eliminan los hijos
                                borraHijos(seccionAlternativas)
                                idAlternativas=""
                                for cadaAlternativa in combinacionAlternativas:
                                    #Se agregan los distractores al xml
                                    idAlternativas+=agregaAlternativaIteracion(seccionAlternativas,cadaAlternativa)+" "
                                #Se agrega la alternativa solucion 
                                idAlternativas+=agregaAlternativaIteracion(seccionAlternativas,alternativaSolucion)
                                #Genero el xml
                                contador+=1
                                xmlSalida.escribePlantilla(kwuargs['directorioSalida'],xmlEntradaObject.tipo,idItem+"@"+idAlternativas,plantillaSalida,'xml')
    print str(contador)+' Creados'

# Declaracion de directorio de entradas
nombreDirectorioEntradas="./Entradas/Definiciones"
nombreDirectorioPlantillas="./Plantillas"
nombreDirectorioSalidas="Salidas"
nombreCompilador="python"
tipoPregunta='pythonCompara'
listaXmlEntrada=list()

if nombres.validaExistenciasSubProceso(nombreDirectorioEntradas)==True:
    listaXmlEntrada=xmlSalida.lecturaXmls(nombreDirectorioEntradas, tipoPregunta)

for cadaXmlEntrada in listaXmlEntrada:
    retornaPlantilla(nombreDirectorioPlantillas, cadaXmlEntrada, cadaXmlEntrada.cantidadAlternativas,tipoPregunta, directorioSalida=nombreDirectorioSalidas+'/'+tipoPregunta)