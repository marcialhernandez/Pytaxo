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

import os, sys,subprocess, hashlib, itertools, ast, json,argparse
sys.path.insert(0, os.getcwd())
from archivos import nombres, xmlSalida, acceso 
from clases import plantilla, alternativa


try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

def borraHijos(ETObject):
    for elem in ETObject.getchildren():
        ETObject.remove(elem)
    pass

def generaAlternativas(banderaTodas,puntaje,pozoOpciones):
    #Aqui es donde se generan las alternativas tipo alternativa
    #Se generan el pozo de alternativas distractoras y la alternativa solucion
    listaAlternativasDistractoras=[]
    alternativaSolucion=""
    if banderaTodas==0:
        alternativaSolucion=alternativa.alternativa("Ninguna", "solucion", puntaje,"Ninguna")
        listaAlternativasDistractoras.append(alternativa.alternativa("Todas", "distractor", 0,"I, II y III"))                  
        for opcion in pozoOpciones:
            comentario="La funcion "+opcion["glosaAlternativaNumerica"][0]+ " retorna "+ str(opcion["retorno"][0]) + " y la funcion " +opcion["glosaAlternativaNumerica"][1]+ " retorna "+ str(opcion["retorno"][1])+"."
            listaAlternativasDistractoras.append(alternativa.alternativa("+".join(opcion["idAlternativa"]),"distractor",0," y ".join(opcion["glosaAlternativaNumerica"]),comentario=comentario))                  
       #La alternativa correcta es "ninguna"
    elif banderaTodas==1:
        #La alternativa correcta es la consulta contenida en pozoOpciones que tiene el atributo "igualdad"==True
        listaAlternativasDistractoras.append(alternativa.alternativa("Ninguna", "distractor", 0,"Ninguna"))                  
        listaAlternativasDistractoras.append(alternativa.alternativa("Todas", "distractor", 0,"I, II y III"))                  
        for opcion in pozoOpciones:
            if opcion["igualdad"]==False:
               comentario="La funcion "+opcion["glosaAlternativaNumerica"][0]+ " retorna "+ str(opcion["retorno"][0]) + " y la funcion " +opcion["glosaAlternativaNumerica"][1]+ " retorna "+ str(opcion["retorno"][1])+"."
               listaAlternativasDistractoras.append(alternativa.alternativa("+".join(opcion["idAlternativa"]),"distractor",0," y ".join(opcion["glosaAlternativaNumerica"]),comentario=comentario))
            else:
               alternativaSolucion=alternativa.alternativa("+".join(opcion["idAlternativa"]),"solucion",puntaje," y ".join(opcion["glosaAlternativaNumerica"]))
    elif banderaTodas==2:
        #La alternativa correcta es "Todas"
        alternativaSolucion=alternativa.alternativa("Todas", "solucion", puntaje,"I, II y III")
        listaAlternativasDistractoras.append(alternativa.alternativa("Ninguna", "distractor", 0,"Ninguna"))                  
        for opcion in pozoOpciones:
            comentario="La funcion "+opcion["glosaAlternativaNumerica"][0]+ " retorna "+ str(opcion["retorno"][0]) + " y la funcion " +opcion["glosaAlternativaNumerica"][1]+ " retorna "+ str(opcion["retorno"][1])+"."
            listaAlternativasDistractoras.append(alternativa.alternativa("+".join(opcion["idAlternativa"]),"distractor",0," y ".join(opcion["glosaAlternativaNumerica"]),comentario=comentario))
    return listaAlternativasDistractoras, alternativaSolucion
       
def agrupaFunciones(funcionesComparadas):
    banderaTodas=0 
    pozoOpciones=[]                           
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
    return pozoOpciones,banderaTodas

def agregaGlosaFunciones(funcionesComparadas):
    contadorFunciones=0
    seccionCodigo=""
    idItem=""
    hashNombres={}
    comentarioItem=""
    
    for funcion in funcionesComparadas:
        contadorFunciones+=1
        idItem+=funcion["codigoBruto"]
        hashNombres[funcion["nombreFuncionPrincipal"]]="I"*contadorFunciones
        seccionCodigo+='<h1>\n'+"Funcion "+hashNombres[funcion["nombreFuncionPrincipal"]]+'</h1>\n<pre><code class="inline">\n'+funcion["codigoBruto"]+'</code></pre><BR>\n\n'
        try:
            comentarioItem+="La funcion "+hashNombres[funcion["nombreFuncionPrincipal"]]+" retorna "+str(funcion["retorno"])+"\n"
        except:
            #--->Con esto muestra mensaje de Error 5 y termina su ejecucion
            exit()
    return seccionCodigo,idItem,hashNombres,comentarioItem

def generaGlosaEntradas(listaEntradasBrutas):
    glosaIntermedia=""
    listaEntradas=listaEntradasBrutas.split(";")
    cantidadEntradas=len(listaEntradas)
    if cantidadEntradas>1:
        contador=0
        for entrada in listaEntradas:
            if contador==0:
                glosaIntermedia+="las entradas son: "+entrada
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

#entrada: Es el diccionario que contiene las entradas y los archivos temporales
#agregaEnunciadoEId(plantillaSalida,idItem,enunciado,generaGlosaEntradas(entrada["entradaBruta"]),codigoEnunciado)
def agregaEnunciadoEId(plantillaSalida,idItem,enunciado,glosaEntrada,codigoEnunciado,comentarioItem):
    for elem in plantillaSalida.iterfind('generalfeedback'):
        plantillaSalida.remove(elem)
    for elem in plantillaSalida.getchildren():
        if elem.tag=='questiontext':
            for elem2 in elem.iterfind('text'):
                for elem3 in elem2.getchildren():
                    elem2.remove(elem3)
                elem2.append(ET.Comment((' --><![CDATA[' + ('<h2>'+enunciado.replace("@entrada",glosaEntrada)+'</h2><BR>\n\n'+codigoEnunciado).replace(']]>', ']]]]><![CDATA[>')) + ']]><!-- '))
                #elem2.text='<![CDATA[<h2>'+enunciado.replace("@entrada",glosaEntrada)+'</h2><BR>'+codigoEnunciado#+']]>'
    generalfeedback=ET.SubElement(plantillaSalida,'generalfeedback')
    generalfeedbackText=ET.SubElement(generalfeedback,'text')
    generalfeedbackText.text=comentarioItem

def ejecutaPyTemporal(archivoTemporal):
    nombreTemporal=archivoTemporal.name
    directorioTemporal=nombreTemporal.split("/")
    directorioTemporal.pop()
    directorioTemporal='/'.join(directorioTemporal)
    directorioTemporal=nombres.directorioReal(directorioTemporal)
    p = subprocess.Popen(["python",nombreTemporal],stdout=subprocess.PIPE, cwd=directorioTemporal)
    return str(p.communicate()[0]) #obtiene solo los resultados y no los errores 

def agregaAlternativa(ETObject,alternativaObject):
    seccionAlternativa=ET.SubElement(ETObject,'answer')
    seccionAlternativaText=ET.SubElement(seccionAlternativa,'text')
    seccionAlternativaFeedback=ET.SubElement(seccionAlternativa,'feedback')
    seccionAlternativaFeedbackText=ET.SubElement(seccionAlternativaFeedback,'text')
    seccionAlternativaText.append(ET.Comment((' --><![CDATA[' + ('<body style="font-family:Tahoma, Geneva, sans-serif;font-size:length" >'+alternativaObject.glosa.replace("<","&lt;").replace("'None'","'None' (que significa que nunca fue asignado)")+'</body><BR>').replace(']]>', ']]]]><![CDATA[>')) + ']]><!-- '))
    #seccionAlternativaText.text=alternativaObject.glosa
    seccionAlternativa.set('id', alternativaObject.llave)
    seccionAlternativa.set('tipo',alternativaObject.tipo)
    seccionAlternativa.set('puntaje',str(alternativaObject.puntaje))
    if hasattr(alternativaObject, 'comentario'):
        seccionAlternativaFeedbackText.text="Resultado Alternativa: "+str(alternativaObject.comentario)
    if alternativaObject.tipo=="solucion":
        seccionAlternativa.set('fraction',"100")
        return "s."+alternativaObject.llave
    else:
        seccionAlternativa.set('fraction',"0")
        return "d."+alternativaObject.llave

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
            #plantillasValidas.append(arbolXmlPlantillaEntrada)
            plantillasValidas.append(plantilla.plantilla(tipoPregunta,enunciado.rstrip(),id,taxo=taxonomia))
            validaPlantilla=False
    return plantillasValidas

def unificaAlternativaDistractora(listaAlternativaObject):
    if len(listaAlternativaObject)==1:
        return listaAlternativaObject[0]
    else:
        nuevaLlave=listaAlternativaObject[0].llave+"_"+listaAlternativaObject[1].llave
        nuevaGlosa=str(listaAlternativaObject[0].glosa)+" y "+str(listaAlternativaObject[1].glosa)
        nuevoComentario=str(listaAlternativaObject[0].comentario)+" y "+str(listaAlternativaObject[1].comentario)
        return alternativa.alternativa(nuevaLlave,"distractor",0,nuevaGlosa,comentario=nuevoComentario)
    
def unificaAlternativaSolucion(listaAlternativaObject,puntaje):
    if len(listaAlternativaObject)==1:
        return listaAlternativaObject[0]
    else:
        nuevaLlave=listaAlternativaObject[0].llave+"_"+listaAlternativaObject[1].llave
        nuevaGlosa=str(listaAlternativaObject[0].glosa)+" y "+str(listaAlternativaObject[1].glosa)
        nuevoComentario=str(listaAlternativaObject[0].comentario)
        return alternativa.alternativa(nuevaLlave,"solucion",puntaje,nuevaGlosa,comentario=nuevoComentario)

def retornaPlantilla(nombreDirectorioPlantillas,xmlEntradaObject,cantidadAlternativas, tipoPregunta,raiz,formato,estilo, **kwuargs): #,xmlEntradaObject):
    #Cuenta la cantidad de items generados
    contador=0
    banderaEstado=False
    cantidadFuncionesAComparar=3 #Siempre son 3, pues si fuesen 2 no se generarian alternativas suficientes
    if 'directorioSalida' in kwuargs.keys():
        banderaEstado=True #Indica si se debe imprimir o no el estado de la cantidad de salidas
    for plantilla in recogePlantillas(nombreDirectorioPlantillas,tipoPregunta):
        if xmlEntradaObject.linkPlantilla(plantilla)==False:
            continue
        plantillaSalida=xmlSalida.plantillaGenericaSalida(xmlEntradaObject.puntaje,xmlEntradaObject.shuffleanswers,xmlEntradaObject.penalty,xmlEntradaObject.answernumbering)
        plantillaSalida.set('tipo',xmlEntradaObject.tipo)
        plantillaSalida.set('idOrigenEntrada',xmlEntradaObject.idOrigenEntrada)
        plantillaSalida.set('taxonomia',plantilla.taxo)
        print ("todoOK")
        for entrada in xmlEntradaObject.codigos:
            #print entrada["entradaBruta"]
            
            #Se evalua cada codigo con la entrada actual
            for codigoCondicionalAsociado in entrada["codigosCondicionales"]:
                streamTraza=obtieneTraza(ejecutaPyTemporal(codigoCondicionalAsociado["archivo"]))
                if len(streamTraza)>0:
                     codigoCondicionalAsociado["retorno"]=streamTraza[-1]['retorno']
                else:
                    print "Error 5: La condicion '",codigoCondicionalAsociado["condicion"],"' no admite la entrada '",entrada["entrada"]+"'"
                    del codigoCondicionalAsociado

            solucionesModeladas=[]    
            for pivoteSolucion in range(len(entrada["codigosCondicionales"])):
                if entrada["codigosCondicionales"][pivoteSolucion]["retorno"] in solucionesModeladas:
                    continue
                solucionesModeladas.append(entrada["codigosCondicionales"][pivoteSolucion]["retorno"])
                soluciones=[]
                soluciones2=[]
                distractores=[]
                distractores2=[]
                #soluciones.append(entrada["codigosCondicionales"][pivoteSolucion])
                soluciones.append(alternativa.alternativa("temp","solucion",xmlEntradaObject.puntaje,str(list(entrada["codigosCondicionales"][pivoteSolucion]["condicion"])),comentario=entrada["codigosCondicionales"][pivoteSolucion]["retorno"]))
                #print "solucion",soluciones[0]["retorno"]
                #print "___________"
                #print "distractores...."
                for cinta in range(len(entrada["codigosCondicionales"])):
                    #print entrada["codigosCondicionales"][cinta]["retorno"]
                    if cinta!=pivoteSolucion and soluciones[0].comentario!=entrada["codigosCondicionales"][cinta]["retorno"]:
                        #alternativa.alternativa(idAlternativa,"distractor",0,enunciadoAlternativa,comentario=comentarioAlternativa))
                        #distractores.append([entrada["codigosCondicionales"][cinta]])
                        distractores.append(alternativa.alternativa("temp","distractor",0,str(list(entrada["codigosCondicionales"][cinta]["condicion"])),comentario=entrada["codigosCondicionales"][cinta]["retorno"]))
                    elif cinta!=pivoteSolucion and soluciones[0].comentario==entrada["codigosCondicionales"][cinta]["retorno"]:
                        soluciones.append(alternativa.alternativa("temp","solucion",xmlEntradaObject.puntaje,str(list(entrada["codigosCondicionales"][cinta]["condicion"])),comentario=entrada["codigosCondicionales"][cinta]["retorno"]))
                
                for element in list(itertools.product(soluciones, distractores)):
                    distractores2.append(unificaAlternativaDistractora(element))
#                     pass
#                 for alternativaD in distractores:
#                     print alternativaD.imprimeAlternativa()
#                 print "AAAAAAAAAAAAA"
                for element in list(itertools.combinations(soluciones, 2)):
                    soluciones2.append(unificaAlternativaSolucion(element,xmlEntradaObject.puntaje))
                soluciones=acceso.union(soluciones,soluciones2)
                distractores=acceso.union(distractores,distractores2)
                pozoDistractores=[]    
                for grupoAlternativasDistractoras in list(itertools.combinations(distractores, cantidadAlternativas)):
                    pozoDistractores.append(list(grupoAlternativasDistractoras))
                
                #Falta poner una validacion sobre el largo del pozo de de distractores
                
                for cadaAlternativaSolucion in soluciones:
                    
                    #Se agrega enunciado
                    enunciado=plantilla.enunciado[:].replace("@termino","'"+xmlEntradaObject.terminoAPreguntar+"'")
                    enunciado=enunciado.replace("@valor","'"+str(cadaAlternativaSolucion.comentario)+"'")
                    enunciado=enunciado.replace("@entrada",generaGlosaEntradas(entrada["entradaBruta"]))
                    enunciadoTexto='<body style="font-family:Tahoma, Geneva, sans-serif;font-size:length" >'+enunciado+'</body><BR>'
                    enunciadoCodigo='<pre id="python" class="prettyprint linenums">'+xmlEntradaObject.seccionCondicionIncompleto.replace("<","&lt;")+'</pre>'
                 
                    for subRaizSalida in plantillaSalida.iter():
                        if subRaizSalida.tag=='questiontext':
                            for elem in subRaizSalida.iterfind('text'):
                                    
                                for elem3 in elem.getchildren():
                                    elem.remove(elem3)
                                #elem.text=xmlEntradaObject.enunciado
                                elem.append(ET.Comment((' --><![CDATA[' + ('<script src="https://google-code-prettify.googlecode.com/svn/loader/run_prettify.js?skin=sons-of-obsidian"></script>'+enunciadoTexto+enunciadoCodigo).replace(']]>', ']]]]><![CDATA[>')) + ']]><!-- '))
                    
                    idAlternativas=""
                    for cadaGrupoDistractores in pozoDistractores:
                        
                        for elem in plantillaSalida.getchildren():
                            if elem.tag=='answer':
                                plantillaSalida.remove(elem)
                        #Se agregan los distractores al xml
                        idAlternativas+=agregaAlternativa(plantillaSalida,cadaAlternativaSolucion)
                        
                        for cadaDistractor in cadaGrupoDistractores:
                            #Agregar cada distractor al apartado de alternativas
                            idAlternativas+=agregaAlternativa(plantillaSalida,cadaDistractor)
                        
                    contador+=1
                    #id=xmlEntradaObject.idItem(plantilla,tipoPregunta,idAlternativas)
                    #id=xmlEntradaObject.idOrigenEntrada+"-"+idItem+" "+idAlternativas
                    for elem in plantillaSalida.getchildren():
                        if elem.tag=='name':
                            for elem2 in elem.iterfind('text'):
                                elem2.text=tipoPregunta+"_"+plantilla.taxo+"_"+xmlEntradaObject.idOrigenEntrada+"_Pregunta numero "+str(contador)
                    if raiz=='quiz':
                        quiz = ET.Element('quiz')
                        quiz.append(plantillaSalida)
#                         xmlSalida.escribePlantilla2(kwuargs['directorioSalida'],xmlEntradaObject.tipo,id,quiz,'xml',formato,estilo,merge=raiz)
                        xmlSalida.escribePlantilla2(kwuargs['directorioSalida'],xmlEntradaObject.tipo,"Pregunta numero "+str(contador),quiz,'xml',formato,estilo,merge=raiz)
                    else:
                        #xmlSalida.escribePlantilla2(kwuargs['directorioSalida'],xmlEntradaObject.tipo,id,plantillaSalida,'xml',formato,estilo,merge=raiz)
                        xmlSalida.escribePlantilla2(kwuargs['directorioSalida'],xmlEntradaObject.tipo,"Pregunta numero "+str(contador),plantillaSalida,'xml',formato,estilo,merge=raiz)
    print xmlEntradaObject.idOrigenEntrada+"->"+str(contador)+' Creados'
#                         
#         for entrada in xmlEntradaObject.codigos:
#            #Aqui es donde se empiezan a crear las formas de los diferentes tipos de preguntas
#            
#             #cantidadFuncionesAComparar debe ser una entrada!!! del xml!!
#             #Aqui ya se ha duplicado la info
#             for funcionesComparadas in list(itertools.combinations(entrada["codigos"],cantidadFuncionesAComparar)):
#                 #Antes de agregar nueva informacion, se eliminan los hijos
#                 #hasNombres {}:Tabla hashNombres creada para asociar cada funcion a un numero
#                #comentarioItem "": comentario agregado al final, que menciona los retornos de todas las funciones que aparecen en el item
#                #idItem "": id identificador de las funciones que se usan en el item
#                #seccionesCodigo []: referencias que contienen las secciones de cada codigo
#                #Agrego la informacion respecto a las funciones en la glosa del item
#                 codigoEnunciado,idItem,hashNombres,comentarioItem=agregaGlosaFunciones(funcionesComparadas)
#                 idItem=str(hashlib.sha256(idItem).hexdigest())+"@"+entrada["entradaBruta"]  
#                 #Luego se agrega este atributo al tag plantilla, es necesario el for, pues SubRaiz actual es del tag opciones 
#                 agregaEnunciadoEId(plantillaSalida,idItem,plantilla.enunciado[:],generaGlosaEntradas(entrada["entradaBruta"]),codigoEnunciado,comentarioItem.rstrip())
#                 #Ahora se agregan las secciones de alternativas y el comentario, con su respectivo comentario
#                 #seccionAlternativas=ET.SubElement(subRaizSalida,'alternativas')
#                 #Se agrega comentario del item, que menciona el valor de retorno de cada funcion
#                 #seccionComentario=ET.SubElement(subRaizSalida,'solucion')
#                 #seccionComentario.text=comentarioItem.rstrip()
#                 #banderaTodas indica si todas las funciones comparadas son iguales o no, son iguales si es mayor que 1
#                 #Si la banderaTodas es 0, ninguna es igual
#                 #Si la banderaTodas es 1, hay por lo menos una igualdad
#                 #Si la banderaTodas es 2, todas las funciones son iguales entre si
#                 #pozoOpciones: Por cada grupo de 3 funciones a comparar, se separan en grupos de 2 para crear las alternativas 
#                 pozoOpciones,banderaTodas=agrupaFunciones(funcionesComparadas)  
#                                     
#                 #reemplazar los nombres de las funciones principales por sus numeros segun la tabla hash
#                 for opcion in pozoOpciones:
#                     nuevosNombres=[]
#                     for nombreFuncion in opcion["glosaAlternativa"]:
#                         nuevosNombres.append(nombreFuncion.replace(nombreFuncion,hashNombres[nombreFuncion]))
#                     #Estos son los nombres traducidos segun la tabla hash local creada
#                     opcion["glosaAlternativaNumerica"]=nuevosNombres
#                     #print " y ".join(opcion["glosaAlternativaNumerica"])
#                     #print "+".join(opcion["idAlternativa"])
#                 #Se generan el pozo de alternativas distractoras y la alternativa solucion
#                 listaAlternativasDistractoras, alternativaSolucion=generaAlternativas(banderaTodas,xmlEntradaObject.puntaje,pozoOpciones)
#                    
#                 #Ahora se tiene que hacer la combinatoria del pozo de alternativas distractoras (combinaciones de cantidad de alternativas-1) y a cada una de estas, se le agrega la alternativa correcta al final
#                 #Cada grupo generado es una forma distinta
#                 try:
#                     listaCombinacionesAlternativas=list(itertools.combinations(listaAlternativasDistractoras,xmlEntradaObject.cantidadAlternativas-1))
#                 except:
#                     print "Error 4: Este tipo de item no soporta 0 alternativas como argumento de entrada"
#                     exit() 
#                 for combinacionAlternativas in listaCombinacionesAlternativas:
#                     #test=""
#                     #Antes de agregar nueva informacion, se eliminan los hijos
#                     for elem in plantillaSalida.getchildren():
#                         if elem.tag=='answer':
#                             plantillaSalida.remove(elem)
#                     #borraHijos(seccionAlternativas)
#                     idAlternativas=""
#                     for cadaAlternativa in combinacionAlternativas:
#                         #Se agregan los distractores al xml
#                         idAlternativas+=agregaAlternativa(plantillaSalida,cadaAlternativa)+" "
#                     #Se agrega la alternativa solucion 
#                     idAlternativas+=agregaAlternativa(plantillaSalida,alternativaSolucion)
#                     #Genero el xml
#                     contador+=1
#                     id=xmlEntradaObject.idItem(plantilla,tipoPregunta,idAlternativas)
#                     #id=xmlEntradaObject.idOrigenEntrada+"-"+idItem+" "+idAlternativas
#                     for elem in plantillaSalida.getchildren():
#                         if elem.tag=='name':
#                             for elem2 in elem.iterfind('text'):
#                                 elem2.text=id
#                     if raiz=='quiz':
#                         quiz = ET.Element('quiz')
#                         quiz.append(plantillaSalida)
#                         xmlSalida.escribePlantilla2(kwuargs['directorioSalida'],xmlEntradaObject.tipo,id,quiz,'xml',formato,estilo,merge=raiz)
#                     else:
#                         xmlSalida.escribePlantilla2(kwuargs['directorioSalida'],xmlEntradaObject.tipo,id,plantillaSalida,'xml',formato,estilo,merge=raiz)
#     print xmlEntradaObject.idOrigenEntrada+"->"+str(contador)+' Creados'

#Obtencion de argumentos de entrada
parser = argparse.ArgumentParser(description='Argumentos de entrada de Pytaxo')
raiz,formato,estilo=acceso.parserAtributos(parser)
# Declaracion de directorio de entradas
nombreDirectorioEntradas="./Entradas"
nombreDirectorioPlantillas="./Plantillas"
nombreDirectorioSalidas="Salidas"
nombreCompilador="python"
tipoPregunta='condicionalesPython'
listaXmlEntrada=list()

if raiz=='merge':
    xmlSalida.mergeOperation(nombreDirectorioSalidas+'/'+tipoPregunta,tipoPregunta,'xml','open',formato,estilo)
    
if nombres.validaExistenciaArchivo(nombreDirectorioEntradas)==True:
    listaXmlEntrada=xmlSalida.lecturaXmls(nombreDirectorioEntradas, tipoPregunta)

for cadaXmlEntrada in listaXmlEntrada:
    retornaPlantilla(nombreDirectorioPlantillas, cadaXmlEntrada, cadaXmlEntrada.cantidadAlternativas,tipoPregunta,raiz,formato,estilo, directorioSalida=nombreDirectorioSalidas+'/'+tipoPregunta)

if raiz=='merge':
    xmlSalida.mergeOperation(nombreDirectorioSalidas+'/'+tipoPregunta,tipoPregunta,'xml','close',formato,estilo)