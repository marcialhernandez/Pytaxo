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

import itertools, hashlib, copy
from archivos import nombres
from clases import alternativa

class xmlEntrada:
    #atributos estaticos
    
    #atributos de la clase
    def __init__(self,nombre,tipo,puntaje,alternativas,cantidadAlternativas,shuffleanswers,penalty,answernumbering,**kwargs):
        #Atributos en comun
        self.nombre=nombre
        self.tipo=tipo
        self.puntaje=puntaje
        self.alternativas=alternativas
        self.cantidadAlternativas=cantidadAlternativas
        self.shuffleanswers=shuffleanswers
        self.penalty=penalty
        self.answernumbering=answernumbering
        self.id="NULL"
        if 'idOrigenEntrada' in kwargs.keys():
            self.idOrigenEntrada=kwargs['idOrigenEntrada']
        else:
            self.idOrigenEntrada="NULL"
        #Atributos solo de preguntas tipo Definicion
        if self.tipo=="definicion":
            self.termino=kwargs['termino']
            self.id=hashlib.sha256(self.termino).hexdigest()
            #Lista de alternativas de la forma [distractor,{'ponderacion':ponderacion}]
        elif (self.tipo=="pythonTraza" or self.tipo=="pythonIterativo" or self.tipo=="pythonIterativoInvertido") and "codigos" in kwargs.keys():
            self.codigos=kwargs['codigos']

        elif self.tipo=="pythonCompara":
            self.codigos=kwargs['codigos']
            self.comentarios=kwargs['comentarios']

        elif self.tipo=="enunciadoIncompleto":
            #Lista donde cada elemento es parte del enunciado ordenado de forma
            #secuencial
            self.enunciado=kwargs['enunciado']
            self.id=hashlib.sha256(self.enunciado).hexdigest()
            #self.id=hashlib.sha256(self.enunciadoIncompleto).hexdigest()
            #Lista donde cada elemento son las respuestas del enunciado
            #ordenadas de forma secuencial
            #self.respuestas=kwargs['respuestas']
        elif self.tipo=='definicionPareada':
            #La id de este tipo de pregunta se genera cuando tambien lo hace el item
            #Debido a que el ordenamiento de las definiciones expuestas en la parte izquierda
            #Cambian de orden
            self.criterioOrdenDistractores=kwargs['criterioOrdenDistractores']
            self.composicionDistractores=kwargs['composicionDistractores']
            self.ordenTerminos=kwargs['ordenTerminos']
            self.cantidadCombinacionesDefiniciones=kwargs['cantidadCombinacionesDefiniciones']
            self.parcialScore=kwargs['parcialScore']
    
    def printContenidoEntrada(self):
        mensaje="Nombre entrada: {nombre} \nPuntaje: {puntaje}\nTermino: {termino}\nDefinicion: {definicion}\nDistractores: {alternativas} "
        print mensaje.format(nombre=self.nombre,puntaje=self.puntaje, termino=self.termino, definicion=self.definicion,alternativas=self.alternativas)
        pass
    
    #No se sabe si es necesario crear este tipo pues es para un tipo especifico de pregunta
    def preguntaDefSimpleIntoXml(self):
        nombreDirectorioEntradas='./Plantillas'
        if nombres.validaExistenciaArchivo(nombreDirectorioEntradas)==True and nombres.validaCantidadContenido(nombreDirectorioEntradas)==True:
            print nombres.especificDirectoryNames(nombreDirectorioEntradas)
            #falta recoger la informacion y formar la pregunta a partir de la plantilla
        pass
    
    def retornaEnunciadoIncompleto(self):
        return " ".join(self.enunciadoIncompleto)
        
    def retornaAlternativas(self):
        ponderacion={'ponderacion':self.puntaje}
        alternativaCorrecta=list()
        if self.tipo=="definicion":
            alternativaCorrecta.append(self.definicion)
        if self.tipo=="enunciadoIncompleto":
            alternativaCorrecta.append('-'.join(self.respuestas))
        alternativaCorrecta.append(ponderacion)
        alternativas=list()
        alternativas.append(alternativaCorrecta)
        for elem in self.alternativas:
            alternativas.append(elem)
        return alternativas
    #falta reordenar las alternativas pues en este caso siempre la correcta sera la primera
    
    def agrupamientoAlternativas(self,cantidadAlternativas):
        if cantidadAlternativas<=1:
            return list()
        listaDeListaDeAlternativas=list()
        listaDeAlternativasValidas=list()
        for llave in self.alternativas.keys():
            listaDeListaDeAlternativas.append(self.alternativas[llave])
        for posiblesCombinacionesAlternativas in list(itertools.combinations(listaDeListaDeAlternativas,cantidadAlternativas)):
            banderaPresentaACorrecta=False
            for alternativas in posiblesCombinacionesAlternativas:
                if alternativas[0].tipo=='solucion':
                    banderaPresentaACorrecta=True
            if banderaPresentaACorrecta==True:                          
                for posiblesConjuntos in list(itertools.product(*posiblesCombinacionesAlternativas)):
                    listaDeAlternativasValidas.append(posiblesConjuntos)
        #print len(listaDeAlternativasValidas)
        return listaDeAlternativasValidas
    
    def agrupamientoAlternativas2(self,cantidadAlternativas):
        if cantidadAlternativas<=1:
            return list()
        listaDeListaDeAlternativas=[]
        listaDeSoluciones=None
        listaDeAlternativasValidas=[]
        for llave in self.alternativas.keys():
            if self.alternativas[llave][0].tipo=='solucion':
                listaDeSoluciones=self.alternativas[llave]
            else:
                listaDeListaDeAlternativas.append(self.alternativas[llave])      
        for posiblesCombinacionesAlternativas in list(itertools.combinations(listaDeListaDeAlternativas,cantidadAlternativas-1)): 
            posiblesCombinacionesAlternativas=list(posiblesCombinacionesAlternativas)
            posiblesCombinacionesAlternativas.append(listaDeSoluciones)
            try:
                for posiblesConjuntos in list(itertools.product(*posiblesCombinacionesAlternativas)):
                    listaDeAlternativasValidas.append(posiblesConjuntos)
            #Esta falla es producida por un mal nombramiento del atributo tipo en el tag alternativa
            except:
                print "Error1: El atributo tipo contiene un nombre distinto de 'solucion' o 'distractor'"
                exit()
        #print len(listaDeAlternativasValidas)
        return listaDeAlternativasValidas
    
    def agrupamientoEnunciadoIncompleto(self,cantidadAlternativas):
        if cantidadAlternativas<=1:
            return []
        distractores=[]
        listaDeDistractores=[]
        listaDeSoluciones=[]
        listaDeAlternativasValidas=[]
        listaDeListaDeDistractores=[]
        #forma de invertir un diccionario : dict(zip(map.values(), map.keys()))
        #print self.alternativas["respuestas"]
        #print self.alternativas["distractores"]
        #Con idOrden, las listas 
        #Aseguro el orden a medida que se agregan las listas
        combinacionesListas=list(itertools.product([0, 1], repeat=len(self.alternativas["idOrden"].keys())))
        del combinacionesListas[0] #elimina caso solo distractores
        del combinacionesListas[-1] #elimina caso solo soluciones
        
        for llave in range(len(self.alternativas["idOrden"].keys())):
            listaKeySolucion=[]
            listaKeyDistractor=[]
            for alternativaSinonimaCorrecta in self.alternativas["respuestas"][self.alternativas["idOrden"][llave]]:
                listaKeySolucion.append([self.alternativas["idOrden"][llave],alternativaSinonimaCorrecta])
            for alternativaDistractoraCorrecta in self.alternativas["distractores"][self.alternativas["idOrden"][llave]]:
                listaKeyDistractor.append([self.alternativas["idOrden"][llave],alternativaDistractoraCorrecta])
            #Lista de listas de forma [llave,glosa]
            #lo comun es que todas las listas tienen la misma llave, por ejemplo lista 1
            #[llave1,glosa], [llave1,glosa]...
            #lista2
            #[llave2,glosa].....
            listaDeDistractores.append(listaKeyDistractor)
            listaDeSoluciones.append(listaKeySolucion)
        for combinacion in combinacionesListas:
            #print combinacion
            listaTemporal=[]
            contador=0
            for decisionBinaria in combinacion:
                #Se agrega una lista de distractores
                if decisionBinaria==0:
                    listaTemporal.append(listaDeDistractores[contador])
                    contador+=1
                    pass
                #Se agrega una lista de soluciones
                else:
                    listaTemporal.append(listaDeSoluciones[contador])
                    contador+=1
                    pass
            listaDeListaDeDistractores.append(listaTemporal)
        del listaTemporal
        for lista in listaDeListaDeDistractores:
            #Se agrupan usando producto cartesiano, lo que no altera el orden
            for distractor in list(itertools.product(*lista)):
                #print distractor
                #print "________"
                distractores.append(distractor)  
        
        alternativasDistractoras=[]
        alternativasCorrectas=[]
        fraccionPuntajePorSolucion=int(100./len(self.alternativas["idOrden"].keys()))
        
        #Se tiene que llevar cada distractor a formato alternativa
        for distractor in distractores:
            llave=[]
            tipo="distractor"
            puntaje=0 #sera puesto como fraccion de forma inmediata
            glosa=[]
            comentario=[]
            for opcion in distractor:
                if opcion[1]["tipo"]=='solucion':
                    puntaje+=fraccionPuntajePorSolucion
                    llave.append(str(opcion[0])+'.'+opcion[1]["glosa"])
                else:
                    llave.append(str(opcion[0])+'.'+str(opcion[1]["id"]))
                    comentario.append(str(opcion[1]["comentario"]))
                glosa.append(opcion[1]["glosa"])
            alternativasDistractoras.append(alternativa.alternativa("-".join(llave),tipo,puntaje,"-".join(glosa),comentario='-'.join(comentario)))
        #Lista de alternativas solucion
        del distractores
        #for distractor in alternativasDistractoras:
        #    print distractor
        
        #Se tiene que llevar cada solucion a formato alternativa
        for solucion in list(itertools.product(*listaDeSoluciones)):
            llave=[]
            tipo="solucion"
            puntaje=100 #sera puesto como fraccion de forma inmediata
            glosa=[]
            for opcion in solucion:
                llave.append(str(opcion[0])+'.'+opcion[1]["glosa"])
                glosa.append(opcion[1]["glosa"])
            alternativasCorrectas.append(alternativa.alternativa("-".join(llave),tipo,puntaje,"-".join(glosa)))
        #desocupo memoria
        del listaDeDistractores
        del listaDeSoluciones
        del listaDeAlternativasValidas
        del listaDeListaDeDistractores
        conjuntosAlternativas=[]
        for solucion in alternativasCorrectas:
            #conjuntoTemporal=[]
            #La solucion siempre sera la primera opcion
            #conjuntoTemporal.append(solucion)
            for conjuntoAlternativasDistractoras in list(itertools.combinations(alternativasDistractoras,cantidadAlternativas-1)):
                #conjuntoTemporal+=conjuntoAlternativasDistractoras
                #print conjuntoTemporal
                #print "_________"
                conjuntosAlternativas.append([solucion]+list(conjuntoAlternativasDistractoras))
        return conjuntosAlternativas 
    
    def barajaDefiniciones(self):
        return list(itertools.permutations(self.alternativas['terminos'].keys()))
    